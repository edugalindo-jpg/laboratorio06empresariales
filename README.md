# Laboratorio 06 - Portal de Noticias con Django

Proyecto `news_portal` desarrollado para la sesión **GLAB-S06-2026** del curso
Desarrollo de Aplicaciones Empresariales (Tecsup). Implementa el motor de
plantillas de Django con herencia, fragmentos reutilizables, filtros, rutas
nombradas, archivos estáticos y multimedia, y personalización del panel de
administración.

## Tecnologías

| Componente | Versión |
| --- | --- |
| Python | 3.14.7 |
| Django | 5.2.17 |
| Pillow | 12.3.0 |
| Base de datos | SQLite 3 |

## Estructura del proyecto

```text
lab06/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── news/
│   ├── management/
│   │   └── commands/
│   │       └── seed_demo.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html
│   └── news/
│       ├── _article_card.html
│       ├── article_detail.html
│       ├── category_list.html
│       └── home.html
├── static/
│   └── css/
│       └── styles.css
├── media/
│   ├── articles/
│   └── authors/
├── docs/
│   ├── capturas/
│   ├── ENTREGABLE_LABORATORIO_06.docx
│   ├── INFORME_LABORATORIO_06.md
│   ├── resultado_pruebas.txt
│   └── verificacion_http.txt
├── scripts/
│   ├── build_report.py
│   ├── capture_admin.py
│   └── verify_site.py
├── manage.py
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Puesta en marcha

```powershell
cd lab06

# 1. Dependencias
python -m pip install -r requirements.txt

# 2. Base de datos
python manage.py migrate

# 3. Superusuario para el admin
$env:DJANGO_SUPERUSER_PASSWORD='Admin12345!'
python manage.py createsuperuser --noinput `
    --username admin --email admin@tecsup.edu.pe

# 4. Datos de demostración e imágenes generadas con Pillow
python manage.py seed_demo

# 5. Servidor de desarrollo
python manage.py runserver
```

Credenciales de desarrollo del panel:

- Usuario: `admin`
- Contraseña: `Admin12345!`

> La base de datos no se versiona. Las imágenes de demostración de `media/`
> sí se incluyen para que el portal se vea completo al clonar el repositorio;
> el comando `seed_demo` permite regenerarlas.

## Rutas del portal

| Página | Ruta | Nombre de ruta |
| --- | --- | --- |
| Portada | `/` | `news:home` |
| Detalle de noticia | `/article/<slug>/` | `news:article_detail` |
| Listado por categoría | `/category/<slug>/` | `news:category_articles` |
| Administración | `/admin/` | - |

Todas las plantillas generan sus enlaces con `{% url 'news:...' %}`; no hay
direcciones escritas a mano en el HTML.

## Configuración principal

`config/settings.py`:

- `news.apps.NewsConfig` registrada en `INSTALLED_APPS`.
- `TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']`.
- `STATICFILES_DIRS = [BASE_DIR / 'static']`.
- `MEDIA_URL = '/media/'` y `MEDIA_ROOT = BASE_DIR / 'media'`.
- Idioma `es-pe` y zona horaria `America/Lima`.

`config/urls.py` sirve los archivos multimedia durante el desarrollo:

```python
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
```

## Modelos

- **Category**: nombre y slug únicos.
- **Author**: nombres, correo único, biografía y fotografía de perfil.
- **Article**: título, slug, resumen, contenido, imagen destacada, fecha de
  publicación, estado de publicación, autor (FK) y categorías (M2M).

La fecha de publicación usa `auto_now_add=True`. La relación con `Author`
utiliza `on_delete=models.CASCADE` y `related_name='articles'`; la relación con
`Category` usa `related_name='articles'`.

## Plantillas y funcionalidades

- `base.html`: estructura HTML5 común, navegación, pie de página y bloques
  `title`, `content` y `sidebar`.
- `news/_article_card.html`: tarjeta reutilizable incluida con
  `{% include 'news/_article_card.html' with article=article %}` desde la
  portada y desde el listado por categoría.
- `news/home.html`: recorre `articles` con `{% for %}`, muestra el estado vacío
  con `{% empty %}`, formatea la fecha con `date:"d M Y"` y recorta el resumen
  con `truncatewords:20`.
- `news/article_detail.html`: muestra imagen destacada, autor, fecha, contenido
  y categorías; hereda de `base.html`.
- `news/category_list.html`: reutiliza la tarjeta y muestra el nombre de la
  categoría y el número de noticias.

## Administración personalizada

| Entidad | `list_display` | `list_filter` | `search_fields` |
| --- | --- | --- | --- |
| Category | `name`, `slug`, `article_count` | publicaciones | `name`, `slug` |
| Author | `first_name`, `last_name`, `email`, `article_count` | publicaciones | `first_name`, `last_name`, `email`, `bio` |
| Article | `title`, `author`, `published_date`, `is_published`, `category_list` | `is_published`, `published_date`, `categories`, `author` | `title`, `summary`, `content`, `author__last_name` |

También se configuraron `prepopulated_fields`, `filter_horizontal`,
`date_hierarchy` y `list_per_page` para agilizar la gestión de contenido.

## Escapado automático de HTML (CP-04)

La noticia **"Django 5.2 refuerza la seguridad de las aplicaciones web"**
contiene en su cuerpo las etiquetas:

```html
<b>Texto en negrita</b>
<script>alert("XSS")</script>
```

La plantilla las renderiza con `{{ article.content }}` sin el filtro `|safe`.
Django aplica *auto-escaping* y convierte `<` en `&lt;`, `>` en `&gt;` y `"` en
`&quot;`. El navegador muestra el código como texto plano, no lo interpreta y no
ejecuta el script. Esto evita ataques de Cross-Site Scripting (XSS). Si se
necesitara mostrar HTML confiable, habría que sanearlo y usar explícitamente
`|safe` o `{% autoescape off %}`, lo cual no es recomendable para contenido
ingresado por usuarios.

Evidencia: [`docs/capturas/04_escapado_html.png`](docs/capturas/04_escapado_html.png).

## Pruebas automatizadas

```powershell
python manage.py test
```

Resultado actual:

```text
Found 10 test(s).
..........
----------------------------------------------------------------------
Ran 10 tests

OK
```

Matriz de casos:

| ID | Caso | Entrada / acción | Resultado esperado | Estado |
| --- | --- | --- | --- | --- |
| CP-01 | Herencia de plantillas | Navegar de portada a detalle | Header, navegación y footer comunes sin duplicar HTML | PASÓ |
| CP-02 | Reutilización de fragmentos | Cargar portada y categoría | Ambas usan `_article_card.html` | PASÓ |
| CP-03 | Gestión desde el admin | Cambiar el título de una noticia | El cambio se refleja en el portal sin editar código | PASÓ |
| CP-04 | Escapado HTML | Guardar `<b>` y `<script>` en el contenido | Se muestran como texto escapado y no se ejecutan | PASÓ |
| CP-05 | Estado vacío | Quitar todas las noticias publicadas | Se muestra el bloque `{% empty %}` | PASÓ |
| CP-06 | Filtros de plantilla | Consultar la portada | Fecha con `date` y resumen con `truncatewords` | PASÓ |
| CP-07 | Rutas nombradas | Revertir `news:home`, `news:article_detail`, `news:category_articles` | URLs correctas | PASÓ |
| CP-08 | Estáticos | Buscar `css/styles.css` con `static` | Archivo encontrado y servido con HTTP 200 | PASÓ |
| CP-09 | Noticia no publicada | Abrir el detalle de un artículo con `is_published=False` | Respuesta HTTP 404 | PASÓ |
| CP-10 | Relaciones en detalle | Abrir una noticia | Se muestran imagen, autor y categorías | PASÓ |

## Verificación de archivos estáticos y medios

| Recurso | Código HTTP | Content-Type |
| --- | --- | --- |
| `/static/css/styles.css` | 200 | `text/css` |
| `/media/articles/tecsup-inaugura-laboratorio-inteligencia-artificial.jpg` | 200 | `image/jpeg` |

La portada renderiza 6 tarjetas, 6 imágenes desde `/media/articles/` y enlaza
la hoja de estilos desde `/static/css/styles.css`.

La verificación completa se puede repetir con el servidor en ejecución:

```powershell
python scripts/verify_site.py
```

Salida guardada en [`docs/verificacion_http.txt`](docs/verificacion_http.txt).
La salida de las pruebas se conserva en
[`docs/resultado_pruebas.txt`](docs/resultado_pruebas.txt).

## Capturas

| Archivo | Descripción |
| --- | --- |
| [01_portada.png](docs/capturas/01_portada.png) | Portada con las seis noticias y la barra lateral |
| [02_detalle_noticia.png](docs/capturas/02_detalle_noticia.png) | Detalle con imagen, autor y categorías |
| [03_listado_categoria.png](docs/capturas/03_listado_categoria.png) | Listado por categoría reutilizando la tarjeta |
| [04_escapado_html.png](docs/capturas/04_escapado_html.png) | Prueba de escapado automático de HTML |
| [05_admin_articulos.png](docs/capturas/05_admin_articulos.png) | Admin de artículos con filtros y búsqueda |
| [06_admin_categorias.png](docs/capturas/06_admin_categorias.png) | Admin de categorías personalizado |
| [07_admin_autores.png](docs/capturas/07_admin_autores.png) | Admin de autores personalizado |
| [08_portada_sin_resultados.png](docs/capturas/08_portada_sin_resultados.png) | Estado vacío con `{% empty %}` |

## Entregable

- Código fuente completo en este directorio.
- Informe con capturas y casos de prueba:
  `docs/ENTREGABLE_LABORATORIO_06.docx`.
- Versión Markdown del informe: `docs/INFORME_LABORATORIO_06.md`.

La subida al repositorio del equipo y al campus virtual debe realizarse con las
credenciales institucionales correspondientes.
