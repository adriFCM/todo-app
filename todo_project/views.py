from django.http import JsonResponse
from django.db import connections
from django.db.utils import OperationalError


def health(request):
    """
    Basic health check endpoint.

    - status: "ok" if the app is running
    - database: "ok" if DB connection works, otherwise "error"
    """
    db_status = "ok"
    try:
        connections["default"].cursor()
    except OperationalError:
        db_status = "error"

    overall = "ok" if db_status == "ok" else "degraded"

    return JsonResponse(
        {
            "status": overall,
            "database": db_status,
        }
    )
