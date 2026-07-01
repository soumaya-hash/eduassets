from .models import User


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

    if not display and request.user.is_authenticated:
        try:
            display = request.user.get_role_display()
        except Exception:
            display = None

    return {
        'selected_role_display': display,
        'selected_role': request.session.get('selected_role') or (request.user.role if request.user.is_authenticated else None),
    }
