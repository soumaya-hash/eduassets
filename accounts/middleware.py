import threading
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
            # Le contexte de la session doit toujours correspondre au compte
            # authentifié ; il ne peut pas servir à adopter le rôle d'un tiers.
            if (
                request.session.get('selected_access_level') != request.user.niveau_acces
                or request.session.get('selected_role') != request.user.role
            ):
                request.session['selected_access_level'] = request.user.niveau_acces
                request.session['selected_role'] = request.user.role
                request.session.save()
        
        response = self.get_response(request)
        return response
