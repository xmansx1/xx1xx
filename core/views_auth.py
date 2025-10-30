# core/views_auth.py
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View
from django.db import transaction

from .forms import VolunteerSignupForm, OrganizationSignupForm
from .models import Volunteer, Organization

class VolunteerSignupView(View):
    template_name = "auth/signup_volunteer.html"

    def get(self, request):
        return render(request, self.template_name, {"form": VolunteerSignupForm()})

    @transaction.atomic
    def post(self, request):
        form = VolunteerSignupForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["name"][:30],  # اختياري
        )
        # ربط الملف التعريفي Volunteer
        Volunteer.objects.create(
            user=user,
            name=form.cleaned_data["name"],
            city=form.cleaned_data["city"],
            skills=form.cleaned_data.get("skills") or [],
        )
        login(request, user)
        messages.success(request, "تم إنشاء حساب المتطوع بنجاح.")
        return redirect("dashboard")


class OrganizationSignupView(View):
    template_name = "auth/signup_org.html"

    def get(self, request):
        return render(request, self.template_name, {"form": OrganizationSignupForm()})

    @transaction.atomic
    def post(self, request):
        form = OrganizationSignupForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        # إنشاء المستخدم
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
            first_name=form.cleaned_data["name"][:30],
        )
        # ربط الملف التعريفي Organization
        Organization.objects.create(
            user=user,
            name=form.cleaned_data["name"],
            city=form.cleaned_data["city"],
        )
        login(request, user)
        messages.success(request, "تم إنشاء حساب الجهة بنجاح.")
        return redirect("dashboard")
