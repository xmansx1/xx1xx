# core/views.py
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, DetailView
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
from .models import ServiceRequest, Volunteer, Organization

# ===== الصفحة الرئيسية: أهداف + إحصاءات =====
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['goals'] = [
            ('تعزيز التكافل المجتمعي', 'ربط الأسر المحتاجة بالمتطوعين والجهات بسرعة.'),
            ('تطوّع فعّال وآمن', 'تحديد الوقت والمكان والتواصل داخل المنصة.'),
            ('شفافية الأثر', 'توثيق المهام وقياس عدد المستفيدين والمتطوعين.'),
        ]
        ctx['stats'] = {
            'beneficiaries': ServiceRequest.objects.count(),
            'volunteers': Volunteer.objects.count(),
            'orgs': Organization.objects.count(),
            'done_week': ServiceRequest.objects.filter(status='done').count(),
        }
        return ctx

# ===== لوحة المتطوع/الجهة =====
@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        v = getattr(user, 'vol_profile', None)
        o = getattr(user, 'org_profile', None)

        # طلبات مُسنَدة لي
        my_assigned = ServiceRequest.objects.none()
        if v:
            my_assigned = ServiceRequest.objects.filter(assigned_to=v).order_by('-created_at')
        elif o:
            my_assigned = ServiceRequest.objects.filter(assigned_org=o).order_by('-created_at')

        # طلبات متاحة (بانتظار) حسب المدينة/المهارة للمتطوع
        available = ServiceRequest.objects.filter(status='pending')
        if v:
            available = available.filter(city=v.city)
            if v.skills:
                available = available.filter(type__in=v.skills)
        elif o:
            available = available.filter(city=o.city)

        ctx['is_vol'] = bool(v)
        ctx['is_org'] = bool(o)
        ctx['my_assigned'] = my_assigned[:50]
        ctx['available'] = available[:50]
        return ctx

# ===== تفاصيل الطلب + حماية الوصول =====
@method_decorator(login_required, name='dispatch')
class RequestDetailView(DetailView):
    model = ServiceRequest
    template_name = 'request_detail.html'
    context_object_name = 'obj'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        v = getattr(user, 'vol_profile', None)
        o = getattr(user, 'org_profile', None)

        allowed = (request.user.is_staff) or \
                  (v and obj.assigned_to_id == v.id) or \
                  (o and obj.assigned_org_id == o.id)

        if not allowed:
            return HttpResponseForbidden("لا تملك صلاحية عرض هذا الطلب.")
        return super().dispatch(request, *args, **kwargs)
