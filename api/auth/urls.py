from django.urls import path
from .views import (SignUpView, ResendActivationView, ActivationView,
                    LoginView, LogoutView, ChangePasswordView, ChangeEmailView,
                    PasswordResetView, PasswordResetConfirmView)

from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='user_signup'),
    path('login/', LoginView.as_view(), name='user_login'),
    path('resend/', ResendActivationView.as_view(), name='user_resend'),
    path('activate/', ActivationView.as_view(), name='user_activate'),
    path('logout/', LogoutView.as_view(), name='user_logout'),
    path('change_password/', ChangePasswordView.as_view(),
         name='change_password'),
    path('change_email/', ChangeEmailView.as_view(), name='change_email'),
    path('reset_password/', PasswordResetView.as_view(),
         name='reset_password'),
    path('reset_password_confirm/', PasswordResetConfirmView.as_view(),
         name='reset_password_confirm')
]
