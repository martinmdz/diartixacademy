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


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.validated_data["user"]
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
        return Response(UserSerializer(request.user).data)


class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role not in ('admin', 'superadmin', 'owner'):
            return Response({"detail": "No autorizado."}, status=403)
        users = User.objects.all().order_by('-date_joined').values(
            'id', 'email', 'username', 'role',
            'date_joined', 'last_login', 'is_active'
        )
        return Response(list(users))


class ChangeRoleView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    ROLES_VALIDOS = ('superadmin', 'owner', 'admin', 'staff', 'instructor', 'cliente')

    def post(self, request, pk):
        if request.user.role not in ('admin', 'superadmin', 'owner'):
            return Response({"detail": "No autorizado."}, status=403)
        new_role = request.data.get('role', '').strip()
        if new_role not in self.ROLES_VALIDOS:
            return Response({"detail": f"Rol inválido."}, status=400)
        try:
            user = User.objects.get(pk=pk)
            if user.role == 'superadmin' and request.user.role != 'superadmin':
                return Response({"detail": "No podés cambiar el rol de un superadmin."}, status=403)
            user.role = new_role
            user.save()
            return Response({"detail": f"Rol actualizado a {new_role}.", "role": new_role})
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=404)


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({"detail": "Email requerido."}, status=400)
        try:
            user = User.objects.get(email=email)
            uid   = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
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
            return Response({"detail": "Contraseña debe tener al menos 6 caracteres."}, status=400)
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