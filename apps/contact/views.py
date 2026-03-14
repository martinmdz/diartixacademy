from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import RedSocial, MensajeContacto
from rest_framework import serializers

class RedSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RedSocial
        fields = ("id", "tipo", "label", "url", "oculto", "orden")

class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MensajeContacto
        fields = ("email", "mensaje")

class RedesSocialesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        redes = RedSocial.objects.filter(oculto=False)
        return Response(RedSocialSerializer(redes, many=True).data)

class MensajeContactoView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = MensajeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response({"detail": "Mensaje enviado."}, status=status.HTTP_201_CREATED)