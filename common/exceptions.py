import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class AppError(Exception):
    code = 'error'
    status_code = 400

    def __init__(self, message=None):
        self.message = message or 'An error occurred.'
        super().__init__(self.message)


class NotFoundError(AppError):
    code = 'not_found'
    status_code = 404


class ValidationError(AppError):
    code = 'validation_error'
    status_code = 400


class ConflictError(AppError):
    code = 'conflict'
    status_code = 409


class PermissionDeniedError(AppError):
    code = 'forbidden'
    status_code = 403


class ServiceUnavailableError(AppError):
    code = 'service_unavailable'
    status_code = 503


def _error_response(message, http_status, data=None):
    return Response(
        {
            'success': False,
            'code': http_status,
            'message': message,
            'data': data,
        },
        status=http_status,
    )


def custom_exception_handler(exc, context):
    if isinstance(exc, AppError):
        return _error_response(exc.message, exc.status_code)

    response = drf_exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled exception in %s", context.get('view'))
        return _error_response(
            'An unexpected error occurred.',
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(response.data, dict) and list(response.data.keys()) == ['detail']:
        detail = response.data['detail']
        return _error_response(str(detail), response.status_code)

    return _error_response('Invalid input.', response.status_code, data=response.data)
