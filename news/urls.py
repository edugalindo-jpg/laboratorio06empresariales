"""URL routes for the news application."""

from django.urls import path

from . import views

app_name = "news"

urlpatterns = [
    path("", views.home_view, name="home"),
    path(
        "article/<slug:slug>/",
        views.article_detail_view,
        name="article_detail",
    ),
    path(
        "category/<slug:slug>/",
        views.category_list_view,
        name="category_articles",
    ),
]
