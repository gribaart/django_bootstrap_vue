from django.urls import path
from jana.utils.decorators import logged_in
from jana.views import RoleView

ajax_patterns = [
              path("role/", logged_in(RoleView.as_view()), name="nz_role_view"),
]
