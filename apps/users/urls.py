from django.urls import path
from . import views

urlpatterns = [
    path("register/",                     views.RegisterView.as_view()),
    path("login/",                        views.LoginView.as_view()),
    path("logout/",                       views.LogoutView.as_view()),
    path("me/",                           views.MeView.as_view()),
    path("users/",                        views.UserListView.as_view()),
    path("users/<int:pk>/change-role/",   views.ChangeRoleView.as_view()),
    path("users/<int:pk>/update-email/",  views.UpdateEmailView.as_view()),
    path("users/<int:pk>/delete/",        views.DeleteUserView.as_view()),
    path("users/<int:pk>/toggle-active/", views.ToggleActiveView.as_view()),
    path("admin/create-user/",            views.AdminCreateUserView.as_view()),
    path("password-reset/",               views.PasswordResetRequestView.as_view()),
    path("password-reset/confirm/",       views.PasswordResetConfirmView.as_view()),
]