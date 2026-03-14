from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Categoria, Curso, Favorito
from .serializers import (
    CategoriaSerializer,
    CursoListSerializer,
    CursoDetailSerializer,
    CursoWriteSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Solo admins pueden escribir, todos pueden leer."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.role == "admin"
        )


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset           = Categoria.objects.all()
    serializer_class   = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        # Los no-admins solo ven categorías visibles
        if not (self.request.user.is_authenticated and self.request.user.role == "admin"):
            qs = qs.filter(oculto=False)
        return qs


class CursoViewSet(viewsets.ModelViewSet):
    queryset           = Curso.objects.select_related("categoria").prefetch_related("bloques").all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ["categoria__key", "destacado", "mas_vendido", "oculto"]
    search_fields      = ["titulo", "descripcion_corta"]
    ordering_fields    = ["titulo", "creado"]
    ordering           = ["-creado"]
    lookup_field       = "slug"   # /api/catalog/cursos/musculos-de-piedra/

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CursoWriteSerializer
        if self.action == 'retrieve':
            return CursoDetailSerializer
        return CursoListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Los no-admins solo ven cursos visibles
        if not (self.request.user.is_authenticated and self.request.user.role == "admin"):
            qs = qs.filter(oculto=False)
        return qs

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def favorito(self, request, slug=None):
        curso = self.get_object()
        fav, created = Favorito.objects.get_or_create(usuario=request.user, curso=curso)
        if not created:
            fav.delete()
            return Response({"favorito": False})
        return Response({"favorito": True})

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def mis_favoritos(self, request):
        ids    = request.user.favoritos.values_list("curso_id", flat=True)
        cursos = Curso.objects.filter(id__in=ids)
        return Response(CursoListSerializer(cursos, many=True).data)


# ── Vistas HTML ──────────────────────────────────────────────────────────────

def index_page(request):
    return render(request, "index.html")


def curso_page(request, slug):
    curso = get_object_or_404(
        Curso.objects.select_related("categoria").prefetch_related("bloques"),
        slug=slug,
        oculto=False,
    )
    return render(request, "curso_detalle.html", {"curso": curso})