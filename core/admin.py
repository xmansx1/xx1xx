# core/admin.py
from django.contrib import admin
from .models import ServiceRequest, Volunteer, Organization

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id','name','city','type','status','date','time','assigned_to','assigned_org','created_at')
    list_filter = ('city','type','status','date')
    search_fields = ('name','phone','desc')

@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('id','name','city','user')
    list_filter = ('city',)
    search_fields = ('name','user__username')

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id','name','city','user')
    list_filter = ('city',)
    search_fields = ('name','user__username')
