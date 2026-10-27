"""Views that render the public pages of the news portal."""

from django.shortcuts import get_object_or_404, render

from .models import Article, Category


def home_view(request):
    """Show every published article, newest first."""
    articles = (
        Article.objects.filter(is_published=True)
        .select_related("author")
        .prefetch_related("categories")
    )
    categories = Category.objects.all()
    context = {
        "articles": articles,
        "categories": categories,
    }
    return render(request, "news/home.html", context)


def article_detail_view(request, slug):
    """Show the full content of a published article."""
    article = get_object_or_404(
        Article.objects.select_related("author").prefetch_related("categories"),
        slug=slug,
        is_published=True,
    )
    categories = Category.objects.all()
    context = {
        "article": article,
        "categories": categories,
    }
    return render(request, "news/article_detail.html", context)


def category_list_view(request, slug):
    """Show the published articles that belong to one category."""
    category = get_object_or_404(Category, slug=slug)
    articles = (
        category.articles.filter(is_published=True)
        .select_related("author")
        .prefetch_related("categories")
    )
    categories = Category.objects.all()
    context = {
        "category": category,
        "articles": articles,
        "categories": categories,
    }
    return render(request, "news/category_list.html", context)
