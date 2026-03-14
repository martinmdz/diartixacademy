from django.urls import path
from . import views

urlpatterns = [
    path("redes/",    views.RedesSocialesView.as_view()),
    path("mensaje/",  views.MensajeContactoView.as_view()),
]