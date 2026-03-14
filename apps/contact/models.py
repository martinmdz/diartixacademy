from django.db import models

class RedSocial(models.Model):
    TIPOS = [("instagram","Instagram"),("whatsapp","WhatsApp"),("facebook","Facebook"),("email","Email"),("otro","Otro")]
    tipo   = models.CharField(max_length=20, choices=TIPOS)
    label  = models.CharField(max_length=100)
    url    = models.CharField(max_length=300)
    oculto = models.BooleanField(default=False)
    orden  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]

class MensajeContacto(models.Model):
    email   = models.EmailField()
    mensaje = models.TextField()
    fecha   = models.DateTimeField(auto_now_add=True)
    leido   = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.email} — {self.fecha:%d/%m/%Y}"