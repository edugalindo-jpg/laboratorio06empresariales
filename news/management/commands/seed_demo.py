"""Load the demo content used in the laboratory report.

Run with::

    python manage.py seed_demo

The command is idempotent: running it again updates the existing records
and regenerates the featured images.
"""

from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from PIL import Image, ImageDraw, ImageFont

from news.models import Article, Author, Category

ARTICLES = [
    {
        "title": "Tecsup inaugura un laboratorio de inteligencia artificial",
        "slug": "tecsup-inaugura-laboratorio-inteligencia-artificial",
        "summary": (
            "El nuevo espacio cuenta con estaciones de trabajo con GPU y "
            "servirá para proyectos de visión por computadora, procesamiento "
            "de lenguaje natural y aprendizaje automático."
        ),
        "content": (
            "Tecsup Digital inauguró un laboratorio de inteligencia artificial "
            "equipado con estaciones de trabajo de alto rendimiento. El espacio "
            "está disponible para estudiantes de las carreras de Desarrollo de "
            "Software, Ciencia de Datos y Redes Digitales.\n\n"
            "Durante la ceremonia de apertura, las autoridades académicas "
            "destacaron que el laboratorio permitirá desarrollar proyectos "
            "vinculados a visión por computadora, procesamiento de lenguaje "
            "natural y modelos predictivos aplicados a la industria.\n\n"
            "Los docentes del área de tecnología coordinarán talleres semanales "
            "y un programa de mentoría para los equipos que participen en "
            "concursos nacionales e internacionales."
        ),
        "author": "valeria-quispe",
        "categories": ["tecnologia", "innovacion"],
        "days_ago": 1,
        "color": "#0b3d5c",
    },
    {
        "title": "Estudiantes de Tecsup ganan el hackatón nacional de innovación",
        "slug": "estudiantes-tecsup-ganan-hackaton-nacional",
        "summary": (
            "Un equipo de cinco estudiantes desarrolló una plataforma que "
            "conecta pequeños agricultores con compradores locales usando "
            "datos satelitales y alertas climáticas."
        ),
        "content": (
            'El equipo "Andes Tech" obtuvo el primer lugar del hackatón '
            "nacional de innovación con una plataforma que ayuda a pequeños "
            "agricultores a planificar sus cosechas y encontrar compradores "
            "locales.\n\n"
            "La solución integra datos satelitales abiertos, alertas climáticas "
            "y un panel de precios de mercado. El jurado valoró la pertinencia "
            "social del proyecto y la calidad de la implementación técnica.\n\n"
            "Los estudiantes recibirán financiamiento para un piloto de tres "
            "meses en la región de Arequipa, acompañados por docentes de la "
            "escuela de Tecnología Digital."
        ),
        "author": "diego-salazar",
        "categories": ["innovacion"],
        "days_ago": 2,
        "color": "#1f6f78",
    },
    {
        "title": "Nuevas becas para carreras tecnológicas en el ciclo 2026",
        "slug": "nuevas-becas-carreras-tecnologicas-2026",
        "summary": (
            "La convocatoria cubre hasta el 80 % de la matrícula para "
            "estudiantes con alto rendimiento académico y vocación por la "
            "transformación digital."
        ),
        "content": (
            "Tecsup abrió la convocatoria de becas para el ciclo 2026, dirigida "
            "a estudiantes interesados en carreras tecnológicas. El programa "
            "cubre hasta el 80 % de la matrícula y contempla un acompañamiento "
            "académico personalizado.\n\n"
            "Los postulantes deberán acreditar un buen rendimiento académico, "
            "participar en una entrevista y presentar una carta de motivación. "
            "La evaluación también considera la participación en proyectos "
            "comunitarios.\n\n"
            "Las inscripciones estarán abiertas hasta el 30 de noviembre. Los "
            "resultados se publicarán en el portal institucional y se "
            "comunicarán por correo electrónico."
        ),
        "author": "camila-torres",
        "categories": ["educacion"],
        "days_ago": 3,
        "color": "#8a4f1d",
    },
    {
        "title": "Django 5.2 refuerza la seguridad de las aplicaciones web",
        "slug": "django-5-2-refuerza-seguridad-aplicaciones-web",
        "summary": (
            "La nueva versión del framework incorpora mejoras en la validación "
            "de formularios, el escapado automático de HTML y la gestión de "
            "archivos estáticos."
        ),
        "content": (
            "La comunidad de Django publicó la versión 5.2 del framework, con "
            "mejoras orientadas a la seguridad y al rendimiento de las "
            "aplicaciones web.\n\n"
            "Entre las novedades destaca el fortalecimiento del escapado "
            "automático de plantillas, que convierte caracteres especiales "
            'como "<" y ">" en entidades HTML seguras. De esta forma se evita '
            "la ejecución de scripts maliciosos en el navegador.\n\n"
            "Los equipos de desarrollo pueden actualizar sus proyectos con "
            "pip y revisar la guía oficial de migración para identificar los "
            "cambios que requieren ajustes.\n\n"
            "Prueba de escapado automático (CP-04): <b>Texto en negrita</b> "
            'y <script>alert("XSS")</script>. Si el navegador muestra las '
            "etiquetas como texto visible, Django está neutralizando el HTML."
        ),
        "author": "valeria-quispe",
        "categories": ["tecnologia", "educacion"],
        "days_ago": 5,
        "color": "#3c4b8a",
    },
    {
        "title": "Aprendizaje basado en proyectos: la nueva ruta formativa",
        "slug": "aprendizaje-basado-proyectos-nueva-ruta-formativa",
        "summary": (
            "Los cursos de tercer ciclo incorporan retos reales de empresas "
            "locales para que los estudiantes construyan portafolios desde el "
            "primer día."
        ),
        "content": (
            "La metodología de aprendizaje basado en proyectos se consolida "
            "como el eje de la formación en Tecnología Digital. Cada curso "
            "incluye un reto planteado por una empresa o institución local.\n\n"
            "Los estudiantes trabajan en equipos multidisciplinarios, aplican "
            "metodologías ágiles y presentan sus resultados ante un jurado de "
            "docentes y especialistas. Al finalizar el ciclo, cada equipo "
            "cuenta con un producto funcional y una demostración documentada.\n\n"
            "Los docentes señalan que este enfoque mejora la motivación, la "
            "comunicación técnica y la capacidad de resolver problemas en "
            "contextos reales."
        ),
        "author": "camila-torres",
        "categories": ["educacion", "innovacion"],
        "days_ago": 7,
        "color": "#4d6b2f",
    },
    {
        "title": "Startup peruana automatiza la gestión de inventarios con IA",
        "slug": "startup-peruana-automatiza-inventarios-ia",
        "summary": (
            "La solución utiliza visión artificial para contar productos y "
            "detectar quiebres de stock en tiendas de abarrotes, reduciendo "
            "errores de inventario hasta en un 40 %."
        ),
        "content": (
            "Una startup peruana presentó una plataforma de gestión de "
            "inventarios que combina cámaras de bajo costo con modelos de "
            "visión artificial. El sistema identifica productos en los "
            "anaqueles y genera alertas cuando detecta stock bajo.\n\n"
            "En las pruebas piloto realizadas en tiendas de abarrotes de Lima, "
            "la herramienta redujo los errores de inventario hasta en un 40 % "
            "y disminuyó el tiempo dedicado a conteos manuales.\n\n"
            "La empresa planea ampliar su operación a provincias y abrir un "
            "programa de prácticas para estudiantes de ingeniería y ciencia "
            "de datos."
        ),
        "author": "diego-salazar",
        "categories": ["innovacion", "tecnologia"],
        "days_ago": 9,
        "color": "#7a3e78",
    },
]

STALE_ARTICLE_SLUGS = ("prueba-seguridad-escapado-automatico-html",)

AUTHORS = [
    {
        "first_name": "Valeria",
        "last_name": "Quispe Rojas",
        "email": "vquispe@tecsup.edu.pe",
        "bio": (
            "Periodista especializada en ciencia y tecnología. Cubre temas de "
            "innovación, inteligencia artificial y transformación digital."
        ),
        "slug": "valeria-quispe",
        "color": "#0b3d5c",
    },
    {
        "first_name": "Diego",
        "last_name": "Salazar Mendoza",
        "email": "dsalazar@tecsup.edu.pe",
        "bio": (
            "Comunicador y analista de tendencias tecnológicas. Escribe sobre "
            "startups, emprendimiento y soluciones digitales."
        ),
        "slug": "diego-salazar",
        "color": "#1f6f78",
    },
    {
        "first_name": "Camila",
        "last_name": "Torres León",
        "email": "ctorres@tecsup.edu.pe",
        "bio": (
            "Redactora de la sección de educación. Sigue de cerca las nuevas "
            "metodologías de enseñanza y los programas de becas."
        ),
        "slug": "camila-torres",
        "color": "#8a4f1d",
    },
]

CATEGORIES = [
    ("Tecnología", "tecnologia"),
    ("Educación", "educacion"),
    ("Innovación", "innovacion"),
]


def _font(size, bold=False):
    names = (
        ("segoeuib.ttf", "arialbd.ttf")
        if bold
        else (
            "segoeui.ttf",
            "arial.ttf",
        )
    )
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _build_article_image(title, category, destination, color):
    width, height = 1200, 675
    base = _hex_to_rgb(color)
    dark = tuple(max(channel - 45, 0) for channel in base)
    image = Image.new("RGB", (width, height), base)
    draw = ImageDraw.Draw(image)

    for y in range(height):
        ratio = y / height
        row = tuple(
            int(dark[channel] * (1 - ratio) + base[channel] * ratio)
            for channel in range(3)
        )
        draw.line([(0, y), (width, y)], fill=row)

    draw.ellipse(
        (850, -190, 1350, 310), fill=tuple(min(channel + 28, 255) for channel in base)
    )
    draw.ellipse(
        (-150, 470, 260, 880), fill=tuple(max(channel - 18, 0) for channel in base)
    )

    category_font = _font(28, bold=True)
    title_font = _font(58, bold=True)
    footer_font = _font(26)

    draw.rounded_rectangle(
        (80, 85, 80 + draw.textlength(category.upper(), font=category_font) + 44, 143),
        radius=29,
        fill="#f2a33a",
    )
    draw.text((102, 98), category.upper(), font=category_font, fill="#07293d")

    lines = _wrap(draw, title, title_font, 980)
    y = 205
    for line in lines[:4]:
        draw.text((80, y), line, font=title_font, fill="#ffffff")
        y += 74

    draw.text(
        (80, height - 92),
        "TECSUP DIGITAL  ·  PORTAL DE NOTICIAS",
        font=footer_font,
        fill=(255, 255, 255, 210),
    )

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "JPEG", quality=90)


def _build_author_image(author, destination, color):
    width = 480
    base = _hex_to_rgb(color)
    image = Image.new("RGB", (width, width), base)
    draw = ImageDraw.Draw(image)
    draw.ellipse(
        (40, 40, width - 40, width - 40),
        fill=tuple(min(channel + 26, 255) for channel in base),
    )
    initials = f"{author['first_name'][0]}{author['last_name'][0]}"
    font = _font(170, bold=True)
    box = draw.textbbox((0, 0), initials, font=font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    draw.text(
        ((width - text_width) / 2, (width - text_height) / 2 - 22),
        initials,
        font=font,
        fill="#ffffff",
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, "JPEG", quality=90)


class Command(BaseCommand):
    help = "Create demo categories, authors, articles and images."

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)

        for slug in STALE_ARTICLE_SLUGS:
            Article.objects.filter(slug=slug).delete()
            stale_image = media_root / "articles" / f"{slug}.jpg"
            if stale_image.exists():
                stale_image.unlink()

        author_by_slug = {}
        category_by_slug = {}

        for name, slug in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name},
            )
            category_by_slug[slug] = category

        for data in AUTHORS:
            image_path = media_root / "authors" / f"{data['slug']}.jpg"
            _build_author_image(data, image_path, data["color"])
            author, _ = Author.objects.update_or_create(
                email=data["email"],
                defaults={
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "bio": data["bio"],
                    "profile_picture": f"authors/{data['slug']}.jpg",
                },
            )
            author_by_slug[data["slug"]] = author

        for data in ARTICLES:
            image_path = media_root / "articles" / f"{data['slug']}.jpg"
            _build_article_image(
                data["title"],
                category_by_slug[data["categories"][0]].name,
                image_path,
                data["color"],
            )
            article, _ = Article.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "summary": data["summary"],
                    "content": data["content"],
                    "featured_image": f"articles/{data['slug']}.jpg",
                    "is_published": True,
                    "author": author_by_slug[data["author"]],
                },
            )
            article.categories.set(
                category_by_slug[slug] for slug in data["categories"]
            )
            published_date = timezone.now() - timedelta(days=data["days_ago"])
            Article.objects.filter(pk=article.pk).update(published_date=published_date)

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data ready: {len(CATEGORIES)} categories, "
                f"{len(AUTHORS)} authors and {len(ARTICLES)} articles."
            )
        )
