"""Automated tests for the news portal laboratory."""

import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path

from django.contrib.staticfiles import finders
from django.core.files.uploadedfile import SimpleUploadedFile
from django.templatetags.static import static
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .models import Article, Author, Category

MEDIA_ROOT = Path(tempfile.mkdtemp(prefix="news-portal-tests-"))


def build_image(filename="featured.jpg"):
    """Return an in-memory JPEG suitable for an ImageField."""
    buffer = BytesIO()
    Image.new("RGB", (320, 180), color="#0b3d5c").save(buffer, "JPEG")
    buffer.seek(0)
    return SimpleUploadedFile(
        filename,
        buffer.read(),
        content_type="image/jpeg",
    )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class NewsPortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.technology = Category.objects.create(
            name="Tecnología",
            slug="tecnologia",
        )
        cls.education = Category.objects.create(
            name="Educación",
            slug="educacion",
        )
        cls.author = Author.objects.create(
            first_name="Valeria",
            last_name="Quispe Rojas",
            email="vquispe@tecsup.edu.pe",
            bio="Periodista de tecnología.",
        )
        cls.published = Article.objects.create(
            title="Noticia publicada de prueba",
            slug="noticia-publicada-de-prueba",
            summary=" ".join(f"palabra{i}" for i in range(1, 31)),
            content=(
                "Contenido seguro. <b>Texto en negrita</b> y "
                '<script>alert("XSS")</script>'
            ),
            featured_image=build_image("published.jpg"),
            author=cls.author,
        )
        cls.published.categories.add(cls.technology, cls.education)
        Article.objects.filter(pk=cls.published.pk).update(
            published_date=timezone.make_aware(datetime(2026, 3, 15, 10, 30))
        )
        cls.published.refresh_from_db()

        cls.unpublished = Article.objects.create(
            title="Noticia no publicada",
            slug="noticia-no-publicada",
            summary="No debe aparecer en el portal.",
            content="Contenido oculto.",
            featured_image=build_image("unpublished.jpg"),
            author=cls.author,
            is_published=False,
        )

    def test_home_uses_base_template_and_card_fragment(self):
        """CP-01 and CP-02: inheritance and reusable card."""
        response = self.client.get(reverse("news:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/home.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "news/_article_card.html")
        self.assertContains(response, 'class="navbar"')
        self.assertContains(response, 'class="article-card"')
        self.assertContains(response, self.published.title)
        self.assertNotContains(response, self.unpublished.title)

    def test_category_page_reuses_card_fragment(self):
        """CP-02: the same card is included in the category listing."""
        url = reverse(
            "news:category_articles",
            kwargs={"slug": self.technology.slug},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/category_list.html")
        self.assertTemplateUsed(response, "news/_article_card.html")
        self.assertContains(response, 'class="article-card"')
        self.assertContains(response, self.published.title)

    def test_home_formats_date_and_truncates_summary(self):
        """The date filter and truncatewords are applied on the home page."""
        response = self.client.get(reverse("news:home"))

        self.assertContains(response, "15 Mar 2026")
        self.assertNotContains(response, "palabra30")

    def test_home_shows_empty_state(self):
        """The empty block is rendered when there are no published articles."""
        Article.objects.all().delete()
        response = self.client.get(reverse("news:home"))

        self.assertContains(
            response,
            "No hay noticias publicadas en este momento.",
        )

    def test_article_detail_renders_relationships(self):
        """Article detail shows image, author and categories."""
        url = reverse(
            "news:article_detail",
            kwargs={"slug": self.published.slug},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, self.published.title)
        self.assertContains(response, "Valeria Quispe Rojas")
        self.assertContains(response, "Tecnología")
        self.assertContains(response, "Educación")
        self.assertContains(response, self.published.featured_image.url)

    def test_unpublished_article_returns_404(self):
        url = reverse(
            "news:article_detail",
            kwargs={"slug": self.unpublished.slug},
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_content_is_html_escaped(self):
        """CP-04: HTML and scripts are escaped by the template engine."""
        url = reverse(
            "news:article_detail",
            kwargs={"slug": self.published.slug},
        )
        response = self.client.get(url)

        self.assertContains(response, "&lt;b&gt;Texto en negrita&lt;/b&gt;")
        self.assertContains(
            response,
            "&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;",
        )
        self.assertNotContains(response, "<b>Texto en negrita</b>")
        self.assertNotContains(response, '<script>alert("XSS")</script>')

    def test_named_routes_are_reversible(self):
        self.assertEqual(reverse("news:home"), "/")
        self.assertEqual(
            reverse(
                "news:article_detail",
                kwargs={"slug": self.published.slug},
            ),
            f"/article/{self.published.slug}/",
        )
        self.assertEqual(
            reverse(
                "news:category_articles",
                kwargs={"slug": self.technology.slug},
            ),
            f"/category/{self.technology.slug}/",
        )

    def test_static_stylesheet_is_found(self):
        self.assertEqual(static("css/styles.css"), "/static/css/styles.css")
        self.assertIsNotNone(finders.find("css/styles.css"))

    def test_admin_reflects_content_changes(self):
        """CP-03: changing data in the database updates the portal."""
        self.published.title = "Título actualizado desde el admin"
        self.published.save(update_fields=["title"])

        response = self.client.get(reverse("news:home"))

        self.assertContains(response, "Título actualizado desde el admin")
        self.assertNotContains(response, "Noticia publicada de prueba")
