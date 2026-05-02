from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

def global_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return response  # DRF already handled it; renderer wraps it

    # Unhandled exception — log and return 500
    logger.exception("Unhandled exception", exc_info=exc)
    return Response(
        {"detail": "An internal error occurred. Our team has been notified."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
