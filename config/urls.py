from django.contrib import admin
from django.urls import path, include
from apps.catalog.views import index_page, curso_page, curso_editor_view

urlpatterns = [
    path("",                      index_page,  name="home"),
    path("admin/",                admin.site.urls),
    path("api/auth/",             include("apps.users.urls")),
    path("api/catalog/",          include("apps.catalog.urls")),
    path("api/contact/",          include("apps.contact.urls")),
    path("cursos/<slug:slug>/editor/",     curso_editor_view,  name="curso-editor"),
    path("cursos/<slug:slug>/",   curso_page,  name="curso_detalle"),
]