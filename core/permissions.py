# core/permissions.py
from typing import Tuple, Optional
from django.contrib.auth.models import User
from .models import Volunteer, Organization, ServiceRequest

def get_actor(user: User) -> Tuple[Optional[Volunteer], Optional[Organization]]:
    """يرجع بروفايل المتطوع/الجهة (أحدهما أو كلاهما None)."""
    vol = getattr(user, "vol_profile", None)
    org = getattr(user, "org_profile", None)
    return (vol, org)

def can_view_request(user: User, obj: ServiceRequest) -> bool:
    """من يمكنه رؤية تفاصيل الطلب؟: المكلّف (متطوع/جهة) أو staff."""
    if user.is_staff:
        return True
    vol, org = get_actor(user)
    if vol and obj.assigned_to_id == vol.id:
        return True
    if org and obj.assigned_org_id == org.id:
        return True
    return False

def can_assign(user: User, obj: ServiceRequest) -> bool:
    """من يحق له قبول/إسناد الطلب لنفسه؟ فقط متطوع/جهة غير مسند لهما والطلب بانتظار."""
    if obj.status != "pending":
        return False
    if obj.assigned_to_id or obj.assigned_org_id:
        return False
    vol, org = get_actor(user)
    return bool(vol or org)

def can_start(user: User, obj: ServiceRequest) -> bool:
    """بدء التنفيذ: المكلّف فقط (متطوع/جهة) وحالة مقبول."""
    if obj.status != "accepted":
        return False
    vol, org = get_actor(user)
    if vol and obj.assigned_to_id == vol.id:
        return True
    if org and obj.assigned_org_id == org.id:
        return True
    return False

def can_complete(user: User, obj: ServiceRequest) -> bool:
    """إنهاء المهمة: المكلّف فقط وحالة قيد التنفيذ."""
    if obj.status != "inprogress":
        return False
    vol, org = get_actor(user)
    if vol and obj.assigned_to_id == vol.id:
        return True
    if org and obj.assigned_org_id == org.id:
        return True
    return False
