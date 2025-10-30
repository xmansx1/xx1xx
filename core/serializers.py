# core/serializers.py
from rest_framework import serializers
from .models import ServiceRequest, Volunteer, Organization

class VolunteerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volunteer
        fields = ['id','name','city','skills','user']

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id','name','city','user']

class ServiceRequestSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    assigned_org_name = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = '__all__'

    def get_assigned_to_name(self, obj):
        return obj.assigned_to.name if obj.assigned_to else None

    def get_assigned_org_name(self, obj):
        return obj.assigned_org.name if obj.assigned_org else None

    def validate_phone(self, v):
        if not v.startswith('05') or not (10 <= len(v) <= 12):
            raise serializers.ValidationError('رقم الجوال غير صالح.')
        return v
