from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group

def user_staff_permission(function):
    def wrap(request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        if user.groups.filter(name='staff').exists():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap