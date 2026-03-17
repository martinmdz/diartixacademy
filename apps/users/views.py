from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User

SUPERADMIN_EMAIL = 'martinmorenomsr@gmail.com'
ROLES_VALIDOS = ('superadmin', 'owner', 'admin', 'staff', 'instructor', 'cliente')
STAFF_ROLES   = ('superadmin', 'owner', 'admin', 'staff', 'instructor')


def _ensure_superadmin(user):
    if user.email == SUPERADMIN_EMAIL and user.role != 'superadmin':
        user.role = 'superadmin'
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['role', 'is_staff', 'is_superuser'])


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        _ensure_superadmin(user)
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]
        _ensure_superadmin(user)
        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({"detail": "Sesión cerrada."})


class MeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "No autenticado."}, status=401)
        _ensure_superadmin(request.user)
        return Response(UserSerializer(request.user).data)


class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        if request.user.role not in ('admin', 'superadmin', 'owner'):
            return Response({"detail": "No autorizado."}, status=403)
        users = User.objects.all().order_by('-date_joined').values(
            'id', 'email', 'username', 'role', 'date_joined', 'last_login', 'is_active'
        )
        return Response(list(users))


class ChangeRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        if request.user.role not in ('admin', 'superadmin', 'owner'):
            return Response({"detail": "No autorizado."}, status=403)
        new_role = request.data.get('role', '').strip()
        if new_role not in ROLES_VALIDOS:
            return Response({"detail": "Rol inválido."}, status=400)
        try:
            user = User.objects.get(pk=pk)
            if user.role == 'superadmin' and request.user.role != 'superadmin':
                return Response({"detail": "No podés cambiar el rol de un superadmin."}, status=403)
            user.role = new_role
            user.is_staff = new_role in STAFF_ROLES
            user.save(update_fields=['role', 'is_staff'])
            return Response({"detail": f"Rol actualizado a {new_role}.", "role": new_role})
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=404)


class UpdateEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        if request.user.role not in ('superadmin', 'owner'):
            return Response({"detail": "No autorizado."}, status=403)
        new_email = request.data.get('email', '').strip()
        if not new_email or '@' not in new_email:
            return Response({"detail": "Email inválido."}, status=400)
        if User.objects.filter(email=new_email).exclude(pk=pk).exists():
            return Response({"detail": "Ese email ya está en uso."}, status=400)
        try:
            user = User.objects.get(pk=pk)
            if user.email == SUPERADMIN_EMAIL and request.user.email != SUPERADMIN_EMAIL:
                return Response({"detail": "No podés cambiar el email del superadmin."}, status=403)
            user.email = new_email
            user.save(update_fields=['email'])
            return Response({"detail": f"Email actualizado a {new_email}.", "email": new_email})
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=404)


class DeleteUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        if request.user.role != 'superadmin':
            return Response({"detail": "Solo el superadmin puede eliminar usuarios."}, status=403)
        try:
            user = User.objects.get(pk=pk)
            if user.email == SUPERADMIN_EMAIL:
                return Response({"detail": "No podés eliminar al superadmin."}, status=403)
            if user.pk == request.user.pk:
                return Response({"detail": "No podés eliminar tu propia cuenta."}, status=403)
            email = user.email
            user.delete()
            return Response({"detail": f"Usuario {email} eliminado."})
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=404)


class ToggleActiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, pk):
        if request.user.role not in ('admin', 'superadmin', 'owner'):
            return Response({"detail": "No autorizado."}, status=403)
        try:
            user = User.objects.get(pk=pk)
            if user.email == SUPERADMIN_EMAIL:
                return Response({"detail": "No podés desactivar al superadmin."}, status=403)
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            return Response({"detail": f"Usuario {'activado' if user.is_active else 'desactivado'}.", "is_active": user.is_active})
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=404)


class AdminCreateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        if request.user.role not in ('superadmin', 'owner'):
            return Response({"detail": "Solo superadmin u owner pueden crear usuarios."}, status=403)
        email    = request.data.get('email', '').strip()
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        role     = request.data.get('role', 'cliente')
        if not email or not username or not password:
            return Response({"detail": "Email, username y password son requeridos."}, status=400)
        if role not in ROLES_VALIDOS:
            return Response({"detail": "Rol inválido."}, status=400)
        if User.objects.filter(email=email).exists():
            return Response({"detail": "Ya existe un usuario con ese email."}, status=400)
        user = User.objects.create_user(email=email, username=username, password=password)
        user.role = role
        user.is_staff = role in STAFF_ROLES
        user.save(update_fields=['role', 'is_staff'])
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({"detail": "Email requerido."}, status=400)
        try:
            user      = User.objects.get(email=email)
            uid       = urlsafe_base64_encode(force_bytes(user.pk))
            token     = default_token_generator.make_token(user)
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
            send_mail(
                subject="Recuperar contraseña",
                message=f"Hola {user.username or user.email},\n\nResetear contraseña:\n{reset_url}\n\nExpira en 24 horas.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except User.DoesNotExist:
            pass
        except Exception:
            return Response({"detail": "Error al enviar email. Configurá EMAIL_HOST_USER en settings."}, status=500)
        return Response({"detail": "Si el email existe, recibirás el link pronto."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        password = request.data.get('password')
        if not all([uid, token, password]):
            return Response({"detail": "Datos incompletos."}, status=400)
        if len(password) < 6:
            return Response({"detail": "La contraseña debe tener al menos 6 caracteres."}, status=400)
        try:
            pk   = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=pk)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Link inválido."}, status=400)
        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Link expirado o inválido."}, status=400)
        user.set_password(password)
        user.save()
        return Response({"detail": "Contraseña actualizada. Ya podés iniciar sesión."})