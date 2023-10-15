# middleware.py
from django.http import HttpResponseForbidden
from django.core.cache import cache

class DistributedRateLimiter:
    def __init__(self, get_response, limit, window_size, client_identifier):
        self.get_response = get_response
        self.limit = limit
        self.window_size = window_size
        self.client_identifier = client_identifier

    def __call__(self, request):
        current_time = int(time.time())
        window_key = f"{self.client_identifier}_window_{current_time // self.window_size}"

        # Use Redis to increment the counter
        current_count = cache.incr(window_key)

        if current_count > self.limit:
            return HttpResponseForbidden("Rate limit exceeded")

        response = self.get_response(request)
        return response
