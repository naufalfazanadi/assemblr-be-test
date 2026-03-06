from rest_framework.views import APIView

from common.response import success
from . import services


class WebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        result = services.process_webhook(request.data)
        message = 'Already processed.' if result == 'skipped' else 'Webhook processed.'
        return success(message=message)
