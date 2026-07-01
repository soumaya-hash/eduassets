from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = False

    def get(self, request, *args, **kwargs):
        # If already authenticated, check if role is selected
        if request.user.is_authenticated:
            # If role already selected, go to dashboard
            if request.session.get('selected_role'):
                return redirect('dashboard')
            # If no role selected, go to role selection
            return redirect('select_role')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        # Redirect to role selection
        return redirect('select_role')


@login_required
def select_role(request):
    """Page to select role after login"""
    # If role already selected, redirect to dashboard
    if request.session.get('selected_role'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        selected_role = request.POST.get('role')
        available_roles = [role[0] for role in User.ROLE_CHOICES]
        
        if selected_role in available_roles:
            request.session['selected_role'] = selected_role
            request.session.save()  # Explicitly save session
            return redirect('dashboard')
    
    context = {
        'roles': User.ROLE_CHOICES,
    }
    return render(request, 'accounts/select_role.html', context)


@login_required
@require_http_methods(["POST"])
def change_session_role(request):
    """Allow changing the role while logged in"""
    new_role = request.POST.get('role')
    available_roles = [role[0] for role in User.ROLE_CHOICES]
    
    if new_role in available_roles:
        request.session['selected_role'] = new_role
        request.session.save()  # Explicitly save session
        from django.contrib import messages
        messages.success(request, 'Rôle changé : {}'.format(dict(User.ROLE_CHOICES).get(new_role, new_role)))
    
    next_url = request.POST.get('next', 'dashboard')
    return redirect(next_url)


@login_required
def profile(request):
    """Display and update the authenticated user's basic profile information."""
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save(update_fields=['email', 'first_name', 'last_name'])
        messages.success(request, 'Votre profil a été mis à jour.')
        return redirect('profile')

    return render(request, 'accounts/profile.html')
