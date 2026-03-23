from django.urls import path
from .views import admin_login, admin_logout

urlpatterns = [
    path("admin-login/", admin_login, name="admin_login"),
    path("admin-logout/", admin_logout, name="admin_logout"),
]