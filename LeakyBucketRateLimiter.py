# middleware.py
import time
from django.http import HttpResponseForbidden
from django.core.cache import cache

class LeakyBucketRateLimiter:
    def __init__(self, get_response, capacity, leak_rate):
        self.get_response = get_response
        self.capacity = capacity
        self.leak_rate = leak_rate

    def __call__(self, request):
        client_identifier = self.get_client_identifier(request)
        current_time = time.time()
        last_access_time = cache.get(client_identifier + "_last_access_time", current_time)
        bucket_tokens = cache.get(client_identifier + "_bucket_tokens", self.capacity)

        # Calculate tokens that should have leaked since the last access
        elapsed_time = current_time - last_access_time
        tokens_to_leak = int(elapsed_time * self.leak_rate)

        # Simulate token leak from the bucket
        bucket_tokens = min(self.capacity, bucket_tokens + tokens_to_leak)

        if bucket_tokens < 1:
            return HttpResponseForbidden("Rate limit exceeded")

        cache.set(client_identifier + "_last_access_time", current_time, None)
        cache.set(client_identifier + "_bucket_tokens", bucket_tokens - 1, None)

        response = self.get_response(request)
        return response

    def get_client_identifier(self, request):
        # Customize this method to extract and return a unique client identifier (e.g., IP address, user ID, API key).
        return request.META.get("REMOTE_ADDR", "anonymous")
