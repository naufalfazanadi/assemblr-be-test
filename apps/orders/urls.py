from django.urls import path
from .views import OrderGetAllCreateView, OrderDetailView, OrderByOrderIdView, OrderPayView

urlpatterns = [
    path('', OrderGetAllCreateView.as_view(), name='order-get-all-create'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<uuid:pk>/pay/', OrderPayView.as_view(), name='order-pay'),
    path('order-id/<str:order_id>/', OrderByOrderIdView.as_view(), name='order-by-order-id'),
]
