from django.contrib import admin
from .models import RedSocial, MensajeContacto

@admin.register(RedSocial)
class RedSocialAdmin(admin.ModelAdmin):
    list_display = ("label", "tipo", "oculto", "orden")

@admin.register(MensajeContacto)
class MensajeContactoAdmin(admin.ModelAdmin):
    list_display = ("email", "fecha", "leido")
    list_filter  = ("leido",)