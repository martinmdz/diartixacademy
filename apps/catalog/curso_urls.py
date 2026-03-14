from django.urls import path
from . import views

urlpatterns = [
    path("", views.curso_page, name="curso_detalle"),
]