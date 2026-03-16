from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from apps.catalog.views import exportar_cursos_excel, importar_cursos_excel

router = DefaultRouter()
router.register("categorias", views.CategoriaViewSet)
router.register("cursos",     views.CursoViewSet)

urlpatterns = router.urls + [
    path("admin/exportar-cursos/", exportar_cursos_excel, name="exportar_cursos"),
    path("admin/importar-cursos/", importar_cursos_excel, name="importar_cursos"),
]