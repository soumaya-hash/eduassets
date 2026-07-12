from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


UserModel = get_user_model()


class CinOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None or password is None:
            return None

        normalized_identifier = UserModel.normalize_cin(username)

        user = None
        if normalized_identifier:
            try:
                user = UserModel._default_manager.get(cin__iexact=normalized_identifier)
            except UserModel.DoesNotExist:
                user = None

        if user is None:
            try:
                user = UserModel._default_manager.get(username=username)
            except UserModel.DoesNotExist:
                return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None