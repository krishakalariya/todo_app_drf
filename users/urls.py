from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterAPI, LoginView, LogoutView

urlpatterns = [
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # Other URL patterns...
]
