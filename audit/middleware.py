from audit.utils import log_activity


class ActivityLogMiddleware:
    """Minimal middleware — actual logging is done in views explicitly."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
