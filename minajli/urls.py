# minajli/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from core.views import HomeView, DashboardView, RequestDetailView
from core.views_api import router as api_router
from core.views_auth import VolunteerSignupView, OrganizationSignupView

urlpatterns = [
    path('admin/', admin.site.urls),

    # مصادقة: دخول/خروج
    path('accounts/login/',  auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # تسجيل جديد
    path('accounts/signup/volunteer/', VolunteerSignupView.as_view(), name='signup_volunteer'),
    path('accounts/signup/org/',       OrganizationSignupView.as_view(), name='signup_org'),

    # صفحات المنصة
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('requests/<int:pk>/', RequestDetailView.as_view(), name='request_detail'),

    # REST API
    path('api/', include(api_router.urls)),
]
