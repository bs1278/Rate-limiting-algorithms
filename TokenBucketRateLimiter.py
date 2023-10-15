# middleware.py
import time
from django.http import HttpResponseForbidden
from django.core.cache import cache

class TokenBucketRateLimiter:
    def __init__(self, get_response, capacity, fill_rate):
        self.get_response = get_response
        self.capacity = capacity
        self.fill_rate = fill_rate

    def __call__(self, request):
        client_identifier = self.get_client_identifier(request)
        current_time = time.time()
        last_refresh = cache.get(client_identifier + "_last_refresh", current_time)
        tokens = cache.get(client_identifier + "_tokens", self.capacity)

        elapsed_time = current_time - last_refresh
        tokens = min(self.capacity, tokens + elapsed_time * self.fill_rate)

        cache.set(client_identifier + "_last_refresh", current_time, None)
        cache.set(client_identifier + "_tokens", tokens, None)

        if tokens < 1:
            return HttpResponseForbidden("Rate limit exceeded")

        cache.decr(client_identifier + "_tokens")
        response = self.get_response(request)
        return response

    def get_client_identifier(self, request):
        # Customize this method to extract and return a unique client identifier (e.g., IP address, user ID, API key).
        return request.META.get("REMOTE_ADDR", "anonymous")
