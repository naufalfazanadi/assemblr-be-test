from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common.exceptions import NotFoundError
from common.response import success


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return success(message='Service is ready.')


def handler404(request, exception=None):
    from common.exceptions import _error_response
    return _error_response('The requested resource was not found.', 'not_found', 404)


def handler500(request):
    from common.exceptions import _error_response
    return _error_response('An unexpected error occurred.', 'server_error', 500)


urlpatterns = [
    path('', HealthCheckView.as_view()),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/products/', include('apps.products.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
]
