import unicodedata
import re
from django.db import models
from django.utils.text import slugify


class Categoria(models.Model):
    key    = models.SlugField(max_length=50, unique=True)
    nombre = models.CharField(max_length=120)
    icono  = models.CharField(max_length=50, blank=True)
    color  = models.CharField(max_length=20, blank=True)
    oculto = models.BooleanField(default=False)
    orden  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Curso(models.Model):
    titulo            = models.CharField(max_length=200)
    slug              = models.SlugField(max_length=220, unique=True)
    descripcion_corta = models.CharField(max_length=300, blank=True)
    descripcion       = models.TextField(blank=True)
    precio            = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    categoria         = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="cursos")
    emoji             = models.CharField(max_length=8, blank=True)
    imagen_banner     = models.URLField(blank=True)
    imagen_card       = models.URLField(blank=True)
    buy_url           = models.URLField(blank=True)
    buy_text          = models.CharField(max_length=60, default="Comprar ahora")
    whatsapp          = models.CharField(max_length=30, blank=True)
    destacado         = models.BooleanField(default=False)
    mas_vendido       = models.BooleanField(default=False)
    oculto            = models.BooleanField(default=False)
    creado            = models.DateTimeField(auto_now_add=True)
    actualizado       = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["-creado"]),
        ]

    def _generar_slug(self):
        """Genera slug a partir del título eliminando acentos correctamente."""
        normalizado = unicodedata.normalize('NFKD', self.titulo)
        sin_acentos = normalizado.encode('ascii', 'ignore').decode('ascii')
        return slugify(sin_acentos)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = self._generar_slug()
            slug = base_slug
            n = 1
            # Evitar slugs duplicados
            while Curso.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class BloqueContenido(models.Model):
    TIPOS = [
        ("descripcion", "Descripción"),
        ("temario",     "Temario"),
        ("testimonio",  "Testimonio"),
        ("imagen",      "Imagen"),
        ("seccion",     "Título de Sección"),
    ]
    curso     = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="bloques")
    tipo      = models.CharField(max_length=20, choices=TIPOS)
    orden     = models.PositiveIntegerField(default=0)
    texto     = models.TextField(blank=True)
    autor     = models.CharField(max_length=100, blank=True)
    estrellas = models.PositiveSmallIntegerField(default=5)
    contenido = models.TextField(blank=True)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.tipo} — {self.curso.titulo}"


class Inscripcion(models.Model):
    usuario = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="inscripciones")
    curso   = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="inscripciones")
    fecha   = models.DateTimeField(auto_now_add=True)
    estado  = models.CharField(
        max_length=20,
        choices=[
            ("pendiente",  "Pendiente"),
            ("pagado",     "Pagado"),
            ("cancelado",  "Cancelado"),
        ],
        default="pagado",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "curso"], name="uniq_usuario_curso")
        ]
        indexes = [
            models.Index(fields=["usuario", "curso"]),
            models.Index(fields=["-fecha"]),
        ]

    def __str__(self):
        return f"{self.usuario} → {self.curso}"


class Favorito(models.Model):
    usuario = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="favoritos")
    curso   = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="favoritos")
    creado  = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["usuario", "curso"], name="uniq_favorito_usuario_curso")
        ]
        indexes = [models.Index(fields=["usuario", "curso"])]

    def __str__(self):
        return f"{self.usuario} ♥ {self.curso}"