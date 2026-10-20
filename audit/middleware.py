from audit.utils import log_activity


class ActivityLogMiddleware:
    """Log authenticated write requests not already explicitly logged by a view."""
    EXCLUDED_PATH_PREFIXES = ('/static/', '/media/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method in ('POST', 'PUT', 'PATCH', 'DELETE')
            and getattr(request, 'user', None) is not None
            and request.user.is_authenticated
            and not request.path.startswith(self.EXCLUDED_PATH_PREFIXES)
            and response.status_code < 500
        ):
            # Keep this generic and avoid recording submitted form contents or PII.
            log_activity(
                request.user,
                'HTTP ' + request.method,
                f'{request.method} {request.path} returned {response.status_code}',
                request,
            )
        return response
