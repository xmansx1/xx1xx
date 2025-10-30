# core/views_dashboard.py
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, View
from .models import ServiceRequest
from .permissions import get_actor, can_view_request, can_assign, can_start, can_complete

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        vol, org = get_actor(user)

        # تبويب: طلبات مناسبة لي (غير مسندة، بانتظار)
        suitable_qs = ServiceRequest.objects.filter(status="pending")
        if vol:
            # التصفية بالمدينة ومطابقة نوع الخدمة إن أحببت لاحقًا، الآن نكتفي بالمدينة
            suitable_qs = suitable_qs.filter(city=vol.city)
        elif org:
            suitable_qs = suitable_qs.filter(city=org.city)
        else:
            suitable_qs = ServiceRequest.objects.none()

        # تبويب: طلباتي المسندة لي (كل الحالات عدا done يُظهر أعلى)
        assigned_q = Q()
        if vol:
            assigned_q |= Q(assigned_to=vol)
        if org:
            assigned_q |= Q(assigned_org=org)

        assigned_qs = ServiceRequest.objects.filter(assigned_q)

        ctx.update({
            "vol": vol, "org": org,
            "suitable_requests": suitable_qs,
            "assigned_requests": assigned_qs,
        })
        return ctx


class RequestDetailView(LoginRequiredMixin, DetailView):
    model = ServiceRequest
    template_name = "requests/request_detail.html"
    context_object_name = "obj"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if not can_view_request(request.user, obj):
            messages.error(request, "ليس لديك صلاحية للاطّلاع على هذا الطلب.")
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)


# -------- الأفعال (POST فقط) --------

class RequestAcceptView(LoginRequiredMixin, View):
    """قبول/إسناد الطلب لنفسي (متطوع/جهة) إذا كان بانتظار وغير مسند."""
    def post(self, request, pk):
        obj = get_object_or_404(ServiceRequest, pk=pk)
        if not can_assign(request.user, obj):
            messages.error(request, "لا يمكن قبول هذا الطلب.")
            return redirect("dashboard")

        vol, org = get_actor(request.user)
        if vol:
            obj.assigned_to = vol
        if org:
            obj.assigned_org = org
        obj.status = "accepted"
        obj.save()
        messages.success(request, "تم قبول الطلب وإسناده لحسابك.")
        return redirect("request_detail", pk=obj.pk)


class RequestStartView(LoginRequiredMixin, View):
    """بدء تنفيذ طلب مُسنَد لي (ينتقل من مقبول إلى قيد التنفيذ)."""
    def post(self, request, pk):
        obj = get_object_or_404(ServiceRequest, pk=pk)
        if not can_start(request.user, obj):
            messages.error(request, "لا يمكن بدء هذا الطلب.")
            return redirect("request_detail", pk=obj.pk)
        obj.status = "inprogress"
        obj.save()
        messages.success(request, "تم بدء تنفيذ الطلب.")
        return redirect("request_detail", pk=obj.pk)


class RequestCompleteView(LoginRequiredMixin, View):
    """إكمال طلب مُسنَد لي (ينتقل من قيد التنفيذ إلى منجز)."""
    def post(self, request, pk):
        obj = get_object_or_404(ServiceRequest, pk=pk)
        if not can_complete(request.user, obj):
            messages.error(request, "لا يمكن إنهاء هذا الطلب.")
            return redirect("request_detail", pk=obj.pk)
        obj.status = "done"
        obj.save()
        messages.success(request, "تم إنهاء الطلب بنجاح.")
        return redirect("request_detail", pk=obj.pk)
