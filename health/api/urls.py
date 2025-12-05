from django.urls import path
from .views import HealthCheckView, chatbot, backend_view

urlpatterns = [
    path('check-health/', HealthCheckView.as_view()),
    # path('chat/', ChatPlaceholderView.as_view()),
    # path('chatbot/', chatbot_page, name="chatbot_page"),
    path('chatbot/', chatbot, name='chatbot'),
    path('backend-view/', backend_view, name="backend_view"),
    # path('ch/', chatbot, name="chatbot")
]