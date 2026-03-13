from django.urls import path
from .views import SearchView, ClearSearchHistoryView, DeleteSearchHistoryView

urlpatterns = [
    path('',                          SearchView.as_view(),              name='search'),
    path('history/clear/',            ClearSearchHistoryView.as_view(),  name='search_history_clear'),
    path('history/<int:pk>/delete/',  DeleteSearchHistoryView.as_view(), name='search_history_delete'),
]