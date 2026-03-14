from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("categorias", views.CategoriaViewSet)
router.register("cursos",     views.CursoViewSet)

urlpatterns = router.urls