from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class BlockedUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            if hasattr(request.user, 'profile') and request.user.profile.is_blocked:
                blocked_url = reverse('blocked_page')
                if request.path != blocked_url:
                    return redirect(blocked_url)
        return None
