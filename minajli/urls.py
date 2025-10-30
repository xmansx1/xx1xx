# minajli/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from core.views import HomeView  # لديك مسبقًا
from core.views_api import router as api_router  # لديك مسبقًا
from core.views_auth import VolunteerSignupView, OrganizationSignupView  # لديك مسبقًا
from core.views_requests import RequestCreateView, RequestThanksView      # من خطوة سابقة
from core.views_dashboard import (
    DashboardView, RequestDetailView,
    RequestAcceptView, RequestStartView, RequestCompleteView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # مصادقة
    path('accounts/login/',  auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # تسجيل
    path('accounts/signup/volunteer/', VolunteerSignupView.as_view(), name='signup_volunteer'),
    path('accounts/signup/org/',       OrganizationSignupView.as_view(), name='signup_org'),

    # عامة
    path('', HomeView.as_view(), name='home'),
    path('request/new/', RequestCreateView.as_view(), name='request_new'),
    path('request/thanks/', RequestThanksView.as_view(), name='request_thanks'),

    # لوحة + تفاصيل
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('requests/<int:pk>/', RequestDetailView.as_view(), name='request_detail'),

    # أفعال الحالة (POST فقط)
    path('requests/<int:pk>/accept/',   RequestAcceptView.as_view(),   name='request_accept'),
    path('requests/<int:pk>/start/',    RequestStartView.as_view(),    name='request_start'),
    path('requests/<int:pk>/complete/', RequestCompleteView.as_view(), name='request_complete'),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),

    # API
    path('api/', include(api_router.urls)),
]
