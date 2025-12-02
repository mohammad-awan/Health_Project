from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({"status": "Ok"})


class ChatPlaceholderView(View):
    def get(self, request):
        return JsonResponse({"message": "Chat endpoint placeholder"})

    def post(self, request):
        return JsonResponse({"message": "Chat endpoint placeholder"})


def error_404(request, exception):
    return JsonResponse(
        {"error": "Route not found"},
        status=404
    )


def error_500(request):
    return JsonResponse(
        {"error": "Internal server error"},
        status=500
    )