"""Django admin configuration for the news portal."""

from django.contrib import admin

from .models import Article, Author, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "article_count")
    list_filter = (("articles__is_published", admin.BooleanFieldListFilter),)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Articles")
    def article_count(self, obj):
        return obj.articles.count()


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "article_count")
    list_filter = (("articles__is_published", admin.BooleanFieldListFilter),)
    search_fields = ("first_name", "last_name", "email", "bio")

    @admin.display(description="Articles")
    def article_count(self, obj):
        return obj.articles.count()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "published_date",
        "is_published",
        "category_list",
    )
    list_filter = ("is_published", "published_date", "categories", "author")
    search_fields = ("title", "summary", "content", "author__last_name")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)
    date_hierarchy = "published_date"
    list_per_page = 10

    @admin.display(description="Categories")
    def category_list(self, obj):
        return ", ".join(category.name for category in obj.categories.all())
