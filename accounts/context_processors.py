from .models import User
from .perimeter import get_selected_access_level, get_allowed_role_codes_for_access_level


def selected_role_display(request):
    """Provide a human-readable selected role for templates.

    Resolves `request.session['selected_role']` (e.g. 'ADMIN') to its
    display label (e.g. 'Administrateur Général') using `User.ROLE_CHOICES`.
    Falls back to the authenticated user's `get_role_display()` if no
    session role is set.
    """
    display = None
    selected_role = None
    try:
        selected_role = request.session.get('selected_role')
    except Exception:
        selected_role = None

    if selected_role:
        choices = dict(User.ROLE_CHOICES)
        display = choices.get(selected_role)

    selected_access_level = get_selected_access_level(request)
    allowed_role_codes = get_allowed_role_codes_for_access_level(selected_access_level)

    if allowed_role_codes:
        available_roles = [choice for choice in User.ROLE_CHOICES if choice[0] in allowed_role_codes]
    else:
        available_roles = User.ROLE_CHOICES

    access_levels = User.ACCESS_LEVEL_CHOICES

    if request.user.is_authenticated:
        allowed_codes = [value for value, _ in available_roles]
        if selected_role not in allowed_codes:
            selected_role = request.user.role

    if not display and request.user.is_authenticated:
        try:
            display = request.user.get_role_display()
        except Exception:
            display = None

    return {
        'selected_role_display': display,
        'selected_role': selected_role or (request.user.role if request.user.is_authenticated else None),
        'available_roles': available_roles,
        'available_access_levels': access_levels,
        'selected_access_level': selected_access_level,
    }
