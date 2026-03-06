from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from common.query import StandardPagination
from common.response import success, paginated_success
from .serializers import OrderSerializer, OrderCreateSerializer, OrderListQuerySerializer
from . import services


class OrderGetAllCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = OrderListQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        orders = services.get_all_orders(
            user=request.user,
            status=query.validated_data.get('status'),
            sort=query.validated_data.get('sort'),
        )
        paginator = StandardPagination()
        page = paginator.paginate_queryset(orders, request)
        return paginated_success(paginator, OrderSerializer(page, many=True).data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.create_order(request.user, serializer.validated_data['items'])
        return success(
            data=OrderSerializer(order).data,
            message='Order created.',
            status_code=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        order = services.get_order_by_pk(pk, request.user)
        return success(data=OrderSerializer(order).data)

    def put(self, request, pk):
        order = services.get_order_by_pk(pk, request.user)
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = services.update_order(order, serializer.validated_data['items'])
        return success(data=OrderSerializer(order).data, message='Order updated.')

    def patch(self, request, pk):
        order = services.get_order_by_pk(pk, request.user)
        order = services.cancel_order(order)
        return success(data=OrderSerializer(order).data, message='Order cancelled.')


class OrderByOrderIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = services.get_order_by_order_id(order_id, request.user)
        return success(data=OrderSerializer(order).data)


class OrderPayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = services.get_order_by_pk(pk, request.user)
        order = services.get_payment_token(order)
        return success(data={
            'midtrans_token': order.midtrans_token,
            'midtrans_redirect_url': order.midtrans_redirect_url,
        })
