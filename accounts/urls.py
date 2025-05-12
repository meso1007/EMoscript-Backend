from django.urls import path
from .views import register_user, login_user, send_password_reset_email, reset_password,admin_user_list,toggle_user_lock, admin_user_list,delete_user,create_payment_intent, activate_premium
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import ProfileView


urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'), 
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password_reset/', send_password_reset_email),
    path('password_reset/confirm/', reset_password),
    path('admin/users/', admin_user_list, name='admin-user-list'),
    path('admin/users/<int:user_id>/toggle-lock/', toggle_user_lock, name='toggle_user_lock'),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('admin/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('payment-intent/', create_payment_intent, name='create-payment-intent'),
    path('activate-premium/', activate_premium, name='activate_premium'),
]