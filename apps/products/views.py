from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.views import APIView

from common.query import StandardPagination
from common.response import success, paginated_success
from .serializers import ProductSerializer, ProductListQuerySerializer
from . import services


class ProductGetAllCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request):
        query = ProductListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        products = services.get_all_products(
            search=query.validated_data.get('search'),
            sort=query.validated_data.get('sort'),
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(products, request)
        return paginated_success(paginator, ProductSerializer(page, many=True).data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = services.create_product(serializer.validated_data)
        return success(
            data=ProductSerializer(product).data,
            message='Product created.',
            status_code=status.HTTP_201_CREATED,
        )


class ProductDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get(self, request, pk):
        product = services.get_product(pk)
        return success(data=ProductSerializer(product).data)

    def put(self, request, pk):
        product = services.get_product(pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        product = services.update_product(product, serializer.validated_data)
        return success(data=ProductSerializer(product).data, message='Product updated.')

    def delete(self, request, pk):
        product = services.get_product(pk)
        services.delete_product(product)
        return success(message='Product deleted.', status_code=status.HTTP_204_NO_CONTENT)
