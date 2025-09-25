from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

from apps.core.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('commerce/', include('apps.commerce.urls')),
    path('api/', include('apps.api.urls')),
    path('settings/', include('apps.settings.urls')),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name='ck_editor_5_upload_file'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)