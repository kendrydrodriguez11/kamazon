from django.urls import path

from apps.settings.views.device import DeviceListView, ForceLogoutView, QRScanView
from apps.settings.views.invoice import InvoiceListView, InvoiceDetailView
from apps.settings.views.product import ProductDeleteView, ProductUpdateView, ProductCreateView, ProductListView
from apps.settings.views.user import UserDetailView, UserUpdateView, UserFaceRegisterView

app_name = 'settings'

urlpatterns = [
    path('profile/', UserDetailView.as_view(), name='profile-detail'),
    path('profile/update/', UserUpdateView.as_view(), name='profile-update'),
    path('profile/facial/', UserFaceRegisterView.as_view(), name='profile-facial'),

    path('devices/', DeviceListView.as_view(), name='profile-devices'),
    path('devices/<int:device_id>/close_session/', ForceLogoutView.as_view(), name='profile-device-close-session'),
    path('devices/scan/', QRScanView.as_view(), name='profile-device-scan'),

    path('products/', ProductListView.as_view(), name='profile-products'),
    path('products/create/', ProductCreateView.as_view(), name='profile-product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='profile-product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='profile-product-delete'),

    path('invoices/', InvoiceListView.as_view(), name='profile-invoices'),
    path('invoices/<int:pk>/detail/', InvoiceDetailView.as_view(), name='profile-invoice-detail'),
]
