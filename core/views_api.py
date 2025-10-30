# core/views_api.py
from rest_framework import viewsets, status, permissions, routers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import ServiceRequest, Volunteer, Organization
from .serializers import ServiceRequestSerializer, VolunteerSerializer, OrganizationSerializer

class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.all()
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.AllowAny]  # للمختبر؛ للإنتاج غيّرها

    def get_queryset(self):
        qs = super().get_queryset()
        city   = self.request.query_params.get('city')
        status_= self.request.query_params.get('status')
        type_  = self.request.query_params.get('type')
        if city:    qs = qs.filter(city=city)
        if status_: qs = qs.filter(status=status_)
        if type_:   qs = qs.filter(type=type_)
        return qs

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        obj = self.get_object()
        to = request.data.get('to')
        allowed = {
            'pending': ['accepted'],
            'accepted': ['inprogress'],
            'inprogress': ['done'],
            'done': [],
        }
        if to not in allowed.get(obj.status, []):
            return Response({'detail': 'انتقال حالة غير مسموح'}, status=status.HTTP_400_BAD_REQUEST)
        obj.status = to
        obj.save()
        return Response(self.get_serializer(obj).data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """إسناد الطلب لمتطوع أو جهة (MVP). للإنتاج: قفلها بالصلاحيات."""
        obj = self.get_object()
        vol_id = request.data.get('volunteer_id')
        org_id = request.data.get('org_id')
        if vol_id:
            try:
                v = Volunteer.objects.get(id=vol_id)
                obj.assigned_to = v
                obj.assigned_org = None
            except Volunteer.DoesNotExist:
                return Response({'detail':'متطوع غير موجود'}, status=404)
        if org_id:
            try:
                o = Organization.objects.get(id=org_id)
                obj.assigned_org = o
                obj.assigned_to = None
            except Organization.DoesNotExist:
                return Response({'detail':'جهة غير موجودة'}, status=404)
        obj.save()
        return Response(self.get_serializer(obj).data)

class VolunteerViewSet(viewsets.ModelViewSet):
    queryset = Volunteer.objects.all()
    serializer_class = VolunteerSerializer
    permission_classes = [permissions.AllowAny]

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.AllowAny]

# Router
router = routers.DefaultRouter()
router.register('requests', ServiceRequestViewSet, basename='requests')
router.register('volunteers', VolunteerViewSet, basename='volunteers')
router.register('orgs', OrganizationViewSet, basename='orgs')
