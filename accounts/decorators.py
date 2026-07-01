from functools import wraps
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
            
            # Get the effective role: session role if set, otherwise user's role
            user_role = request.session.get('selected_role') or request.user.role
            
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator