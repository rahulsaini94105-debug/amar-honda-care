from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class OwnerRequiredMixin(LoginRequiredMixin):
    """Only allow users with OWNER role."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_owner:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class StaffOrOwnerRequiredMixin(LoginRequiredMixin):
    """Allow OWNER and STAFF roles."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in ['OWNER', 'STAFF']:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class MechanicRequiredMixin(LoginRequiredMixin):
    """Allow all authenticated users (mechanic-accessible views)."""
    pass
