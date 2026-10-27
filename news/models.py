"""Data models for the news portal."""

from django.db import models
from django.urls import reverse


class Category(models.Model):
    """Editorial section used to group articles."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("news:category_articles", kwargs={"slug": self.slug})


class Author(models.Model):
    """Person who writes the articles."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="authors/",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ("last_name", "first_name")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Article(models.Model):
    """News story published in the portal."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    summary = models.TextField(help_text="Brief description for news cards")
    content = models.TextField()
    featured_image = models.ImageField(upload_to="articles/")
    published_date = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="articles",
    )
    categories = models.ManyToManyField(Category, related_name="articles")

    class Meta:
        ordering = ("-published_date",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("news:article_detail", kwargs={"slug": self.slug})
