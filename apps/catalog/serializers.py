from rest_framework import serializers
from .models import Categoria, Curso, BloqueContenido, Favorito


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Categoria
        fields = ("id", "key", "nombre", "icono", "color", "oculto", "orden")


class BloqueSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BloqueContenido
        fields = ("id", "tipo", "orden", "texto", "autor", "estrellas", "contenido")


class CursoListSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source="categoria.nombre", read_only=True)
    categoria_key    = serializers.CharField(source="categoria.key",    read_only=True)
    categoria_color  = serializers.CharField(source="categoria.color",  read_only=True)

    class Meta:
        model  = Curso
        fields = (
            "id", "titulo", "slug", "descripcion_corta", "precio",
            "categoria", "categoria_nombre", "categoria_key", "categoria_color",
            "emoji", "imagen_card", "imagen_banner", "buy_url", "buy_text", "whatsapp",
            "destacado", "mas_vendido", "oculto", "creado",
            'page_html', 'page_css', 'page_gjs_data',
        )


class CursoDetailSerializer(CursoListSerializer):
    bloques = BloqueSerializer(many=True, read_only=True)
    page_html     = serializers.CharField(default='',   allow_blank=True)
    page_css      = serializers.CharField(default='',   allow_blank=True)
    page_gjs_data = serializers.JSONField(default=None, allow_null=True)

    class Meta(CursoListSerializer.Meta):
        fields = CursoListSerializer.Meta.fields + ("descripcion", "bloques")
        


class BloqueWriteSerializer(serializers.Serializer):
    """Serializer simple para recibir bloques desde el frontend"""
    tipo      = serializers.CharField()
    orden     = serializers.IntegerField(default=0)
    texto     = serializers.CharField(allow_blank=True, default='')
    autor     = serializers.CharField(allow_blank=True, default='')
    estrellas = serializers.IntegerField(default=5)
    contenido = serializers.CharField(allow_blank=True, default='')


class CursoWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear y editar cursos incluyendo bloques"""
    bloques = BloqueWriteSerializer(many=True, required=False)
    # Campos de lectura para devolver al frontend después de guardar
    categoria_key   = serializers.CharField(source="categoria.key",   read_only=True)
    categoria_nombre= serializers.CharField(source="categoria.nombre", read_only=True)
    categoria_color = serializers.CharField(source="categoria.color",  read_only=True)

    class Meta:
        model  = Curso
        fields = (
            "id", "titulo", "slug", "descripcion_corta", "descripcion", "precio",
            "categoria", "categoria_key", "categoria_nombre", "categoria_color",
            "emoji", "imagen_banner", "imagen_card",
            "buy_url", "buy_text", "whatsapp",
            "destacado", "mas_vendido", "oculto",
            "bloques",
            'page_html', 'page_css', 'page_gjs_data',
        )
        extra_kwargs = {
            'slug':   {'required': False},
            'precio': {'required': False},
        }

    def create(self, validated_data):
        bloques_data = validated_data.pop('bloques', [])
        curso = Curso.objects.create(**validated_data)
        for bloque in bloques_data:
            BloqueContenido.objects.create(curso=curso, **bloque)
        return curso

    def update(self, instance, validated_data):
        bloques_data = validated_data.pop('bloques', None)

        # Actualizar todos los campos del curso
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Si vinieron bloques, borrar los viejos y crear los nuevos
        if bloques_data is not None:
            instance.bloques.all().delete()
            for bloque in bloques_data:
                BloqueContenido.objects.create(curso=instance, **bloque)

        return instance