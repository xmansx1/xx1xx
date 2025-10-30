# core/views_requests.py
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View

from .forms import ServiceRequestPublicForm

class RequestCreateView(View):
    template_name = "requests/request_form.html"

    def get(self, request):
        form = ServiceRequestPublicForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ServiceRequestPublicForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})
        form.save()
        messages.success(request, "تم استلام طلبك، شكرًا لتواصلك.")
        return redirect("request_thanks")


class RequestThanksView(View):
    template_name = "requests/request_thanks.html"

    def get(self, request):
        return render(request, self.template_name)
