from django.urls import path
from .views import SubscribeListView, ToggleSubscriptionView

urlpatterns = [

    # User subscribed channels list
    path(
        "subscriptions/",
        SubscribeListView.as_view(),
        name="subscription_list"
    ),

    # Subscribe / Unsubscribe button
    path(
        "subscribe/<int:channel_pk>/",
        ToggleSubscriptionView.as_view(),
        name="toggle_subscription"
    ),

]