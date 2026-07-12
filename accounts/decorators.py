from functools import wraps
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from .perimeter import get_selected_access_level, get_allowed_role_codes_for_access_level


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
            
            # Get the effective role: session role if set, otherwise user's role
            user_role = request.session.get('selected_role') or request.user.role
            selected_access_level = get_selected_access_level(request)
            allowed_for_user = get_allowed_role_codes_for_access_level(selected_access_level)

            if user_role not in allowed_for_user:
                raise PermissionDenied
            
            if user_role in allowed_roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped_view
    return decorator