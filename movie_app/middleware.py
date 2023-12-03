# middleware.py
from threading import Lock
from django.conf import settings

class RequestCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.lock = Lock()

    def __call__(self, request):
        with self.lock:
            settings.TOTAL_REQUEST_COUNT += 1
            request.total_request_count = settings.TOTAL_REQUEST_COUNT
        response = self.get_response(request)
        return response

   
