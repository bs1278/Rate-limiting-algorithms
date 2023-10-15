# middleware.py
import time
from django.http import HttpResponseForbidden
from django.core.cache import cache

class FixedWindowRateLimiter:
    def __init__(self, get_response, limit, window_size):
        self.get_response = get_response
        self.limit = limit
        self.window_size = window_size

    def __call__(self, request):
        client_identifier = self.get_client_identifier(request)
        current_time = time.time()
        window_start = current_time - self.window_size
        window_key = client_identifier + "_window_start"

        # Get the window start time from cache or set it if not present
        last_window_start = cache.get(window_key, window_start)
        if current_time > last_window_start + self.window_size:
            cache.set(window_key, current_time, None)
            cache.set(client_identifier + "_request_count", 1, None)
        else:
            request_count = cache.get(client_identifier + "_request_count", 0)
            if request_count >= self.limit:
                return HttpResponseForbidden("Rate limit exceeded")

            cache.incr(client_identifier + "_request_count")

        response = self.get_response(request)
        return response

    def get_client_identifier(self, request):
        # Customize this method to extract and return a unique client identifier (e.g., IP address, user ID, API key).
        return request.META.get("REMOTE_ADDR", "anonymous")
