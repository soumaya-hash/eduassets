import threading
from .perimeter import get_selected_access_level, get_allowed_role_codes_for_access_level

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.user = request.user
        response = self.get_response(request)
        return response


class RoleSessionMiddleware:
    """Ensure authenticated users without a selected role are redirected to role selection"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for login, logout, select_role, and admin pages
        protected_paths = [
            '/accounts/login/',
            '/accounts/select_role/',
            '/accounts/logout/',
            '/accounts/password_reset',
            '/admin/',
        ]
        
        # Check if current path is protected
        is_protected = any(request.path.startswith(p) for p in protected_paths)
        
        if not is_protected and request.user.is_authenticated:
            selected_access_level = get_selected_access_level(request)
            allowed_roles = get_allowed_role_codes_for_access_level(selected_access_level)
            selected_role = request.session.get('selected_role')

            if selected_role and allowed_roles and selected_role not in allowed_roles:
                request.session.pop('selected_role', None)
                from django.shortcuts import redirect
                return redirect('select_role')

            # If authenticated but no role selected, redirect to role selection
            if not request.session.get('selected_role'):
                from django.shortcuts import redirect
                return redirect('select_role')
        
        response = self.get_response(request)
        return response
