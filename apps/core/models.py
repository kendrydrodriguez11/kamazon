from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.sessions.models import Session


class ModelBase(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    avatar = models.ImageField(verbose_name='Avatar', upload_to='avatars', null=True, blank=True)
    email = models.EmailField(verbose_name='Email', unique=True)
    phone = models.CharField(verbose_name='Phone', max_length=15, null=True, blank=True)
    direction = models.CharField(verbose_name='Direction', max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return '{}'.format(self.username)

    @property
    def created_at_format(self):
        return self.created_at.strftime('%d/%m/%Y %H:%M:%S')

    @property
    def updated_at_format(self):
        return self.updated_at.strftime('%d/%m/%Y %H:%M:%S')

    @property
    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'users'


class Device(ModelBase):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(verbose_name='IP Address')
    last_activity = models.DateTimeField(auto_now=True)
    os = models.CharField(verbose_name='OS', max_length=50)
    device_type = models.CharField(verbose_name='Device Type', max_length=50)
    location = models.CharField(verbose_name='Location', max_length=255)

    def __str__(self):
        return '{} - {}'.format(self.os, self.device_type)

    class Meta:
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
        db_table = 'devices'
        indexes = [
            models.Index(fields=['user']),
        ]


class FacialData(ModelBase):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='facial_data')
    face_image = models.ImageField(verbose_name='Imagen facial', upload_to='facial_data', null=False)
    is_active = models.BooleanField(verbose_name='Activo', default=True)

    def __str__(self):
        return f'Datos faciales de {self.user.username}'

    class Meta:
        verbose_name = 'Dato facial'
        verbose_name_plural = 'Datos faciales'
        db_table = 'facial_data'
