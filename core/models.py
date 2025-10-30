# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models import Q


# ============================
# الجهات (منظمات/مؤسسات)
# ============================
class Organization(models.Model):
    # ملاحظة: null=True, blank=True لتفادي تعارض UNIQUE أثناء ترحيل SQLite.
    # يمكن لاحقًا جعله إلزاميًا بعد استقرار البيانات.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='org_profile',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=30)

    def __str__(self) -> str:
        return self.name


# ============================
# المتطوعون
# ============================
class Volunteer(models.Model):
    # نفس الملاحظة بخصوص null/blank لتفادي مشاكل الهجرة
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='vol_profile',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    # مثال لقائمة مهارات: ["electric","move","health","senior"]
    skills = models.JSONField(default=list, blank=True)

    def __str__(self) -> str:
        return self.name


# ============================
# طلب الخدمة
# ============================
class ServiceRequest(models.Model):
    TYPE_CHOICES = [
        ('electric', 'تركيب/كهرباء'),
        ('move', 'نقل خفيف'),
        ('health', 'زيارة/توصيل صحي'),
        ('senior', 'مساعدة كبار السن'),
        ('other', 'أخرى'),
    ]
    STATUS_CHOICES = [
        ('pending', 'بانتظار'),
        ('accepted', 'مقبول'),
        ('inprogress', 'قيد التنفيذ'),
        ('done', 'منجز'),
    ]

    # بيانات المستفيد
    name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=20,
        validators=[
            # يبدأ بـ 05 وطول 10–12 رقمًا (مرن للعرض التجريبي)
            RegexValidator(
                regex=r'^05\d{8,10}$',
                message='رقم الجوال غير صالح. يجب أن يبدأ بـ 05 وطول 10–12 رقمًا.'
            )
        ],
        help_text='مثال: 05xxxxxxxx'
    )

    city = models.CharField(max_length=30)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    desc = models.TextField()
    date = models.DateField()
    time = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # إحداثيات اختيارية (للعرض على الخريطة)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # الإسناد (إما متطوع أو جهة — وليس كليهما معًا)
    assigned_to = models.ForeignKey(
        Volunteer,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_requests'
    )
    assigned_org = models.ForeignKey(
        Organization,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_org_requests'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['city']),
            models.Index(fields=['date']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            # منع إسناد الطلب للمتطوع والجهة معًا في آنٍ واحد
            models.CheckConstraint(
                check=~(Q(assigned_to__isnull=False) & Q(assigned_org__isnull=False)),
                name='service_request_single_assignment'
            ),
        ]

    def __str__(self) -> str:
        return f'{self.name} - {self.get_type_display()} - {self.city}'
