# middleware.py
import time
from collections import deque
from django.http import HttpResponseForbidden

class SlidingWindowRateLimiterMiddleware:
    def __init__(self, get_response, window_size, limit):
        self.get_response = get_response
        self.window_size = window_size
        self.limit = limit
        self.window = {}
        
    def __call__(self, request):
        client_identifier = self.get_client_identifier(request)

        if client_identifier not in self.window:
            self.window[client_identifier] = deque(maxlen=self.limit)
        
        current_time = time.time()
        self.window[client_identifier].append(current_time)
        
        if len(self.window[client_identifier]) > self.limit:
            oldest_request_time = self.window[client_identifier][0]
            if current_time - oldest_request_time < self.window_size:
                return HttpResponseForbidden("Rate limit exceeded")
            
        response = self.get_response(request)
        return response

    def get_client_identifier(self, request):
        # Customize this method to extract and return a unique client identifier (e.g., IP address, user ID, API key).
        return request.META.get("REMOTE_ADDR", "anonymous")
