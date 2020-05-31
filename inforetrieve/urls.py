from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.Search.as_view()),
    path("", views.Index.as_view()),
]
