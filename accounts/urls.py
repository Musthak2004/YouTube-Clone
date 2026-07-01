from django.urls import path
from .views import SignUpView, SettingsView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('settings/', SettingsView.as_view(), name='settings'),
]