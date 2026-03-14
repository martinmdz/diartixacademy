from django.contrib import admin
from .models import Categoria, Curso, BloqueContenido, Inscripcion, Favorito

class BloqueInline(admin.TabularInline):
    model = BloqueContenido
    extra = 0

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display  = ("titulo", "categoria", "destacado", "mas_vendido", "oculto", "creado")
    list_filter   = ("categoria", "destacado", "mas_vendido", "oculto")
    search_fields = ("titulo",)
    prepopulated_fields = {"slug": ("titulo",)}
    inlines = [BloqueInline]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "key", "oculto", "orden")
    prepopulated_fields = {"key": ("nombre",)}

admin.site.register(Inscripcion)
admin.site.register(Favorito)