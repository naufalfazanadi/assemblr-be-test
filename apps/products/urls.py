from django.urls import path
from .views import ProductGetAllCreateView, ProductDetailView

urlpatterns = [
    path('', ProductGetAllCreateView.as_view(), name='product-get-all-create'),
    path('<uuid:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
