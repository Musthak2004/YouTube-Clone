from django.urls import path
from .views import SubscriptionListView, ToggleSubscriptionView

urlpatterns = [
    path("", SubscriptionListView.as_view(), name="subscription_list"),
    path("subscribe/<int:channel_pk>/", ToggleSubscriptionView.as_view(), name="toggle_subscription"),
]