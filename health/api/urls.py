from django.urls import path
from .views import HealthCheckView, ChatPlaceholderView


urlpatterns = [
    path('check-health/', HealthCheckView.as_view()),
    path('chat/', ChatPlaceholderView.as_view())
]