# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import ServiceRequest

# -----------------------
# خيارات عامة
# -----------------------
CITY_CHOICES = [
    ('riyadh', 'الرياض'),
    ('jeddah', 'جدة'),
    ('dammam', 'الدمام'),
    ('madinah', 'المدينة'),
    ('makkah', 'مكة'),
]

SKILL_CHOICES = [
    ('electric', 'كهرباء/تركيب لمبة'),
    ('move', 'نقل خفيف'),
    ('health', 'زيارة/توصيل صحي'),
    ('senior', 'مساعدة كبار السن'),
]

BASE_INPUT_CSS = "mt-1 w-full rounded-lg border-slate-300"

# -----------------------
# فورمات التسجيل (كما سلّمنا سابقًا)
# -----------------------
class BaseSignupForm(forms.Form):
    username = forms.CharField(label="اسم المستخدم", max_length=150)
    password1 = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)
    password2 = forms.CharField(label="تأكيد كلمة المرور", widget=forms.PasswordInput)

    name = forms.CharField(label="الاسم الكامل", max_length=120)
    city = forms.ChoiceField(label="المدينة", choices=CITY_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            widget = field.widget
            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = (existing + " " + BASE_INPUT_CSS).strip()

    def clean_username(self):
        u = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=u).exists():
            raise forms.ValidationError("اسم المستخدم مستخدم مسبقًا.")
        return u

    def clean(self):
        data = super().clean()
        p1, p2 = data.get('password1'), data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', "كلمتا المرور غير متطابقتين.")
        if p1:
            try:
                validate_password(p1)
            except forms.ValidationError as e:
                self.add_error('password1', e)
        return data


class VolunteerSignupForm(BaseSignupForm):
    skills = forms.MultipleChoiceField(
        label="المهارات",
        choices=SKILL_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skills"].widget.attrs["class"] = "mt-1 grid grid-cols-1 gap-1"


class OrganizationSignupForm(BaseSignupForm):
    # لا مهارات للجهة في الـ MVP
    pass


# -----------------------
# نموذج “اطلب خدمة” العام
# -----------------------
class ServiceRequestPublicForm(forms.ModelForm):
    # حقل فخ بسيط (honeypot) لمكافحة السبام
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    phone = forms.RegexField(
        label="الجوال",
        regex=r'^05\d{8}$',
        error_messages={"invalid": "الرجاء إدخال رقم سعودي صحيح مثل 05xxxxxxxx"},
    )
    city = forms.ChoiceField(label="المدينة", choices=CITY_CHOICES)

    class Meta:
        model = ServiceRequest
        fields = ["name", "phone", "city", "type", "desc", "date", "time"]
        labels = {
            "name": "الاسم",
            "type": "نوع الخدمة",
            "desc": "الوصف",
            "date": "اليوم",
            "time": "الوقت",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "اسم مقدم الطلب"}),
            "desc": forms.Textarea(attrs={"rows": 3, "placeholder": "اكتب وصفًا مختصرًا للحاجة…"}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _, field in self.fields.items():
            if isinstance(field.widget, forms.HiddenInput):
                continue
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " " + BASE_INPUT_CSS).strip()

    def clean_website(self):
        # أي قيمة => سبام
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("محاولة غير صالحة.")
        return ""

    def clean(self):
        data = super().clean()
        # تحقق من تاريخ اليوم أو بعده
        d = data.get("date")
        t = data.get("time")
        from datetime import date as _date
        if d and d < _date.today():
            self.add_error("date", "لا يمكن اختيار تاريخ في الماضي.")
        if not t:
            self.add_error("time", "الوقت مطلوب.")
        return data

    # إحداثيات تقريبية لكل مدينة (مع انحراف بسيط)
    CITY_GEO = {
        "riyadh":  (24.7136, 46.6753),
        "jeddah":  (21.4858, 39.1925),
        "dammam":  (26.4207, 50.0888),
        "madinah": (24.4709, 39.6122),
        "makkah":  (21.3891, 39.8579),
    }

    def save(self, commit=True):
        import random
        obj: ServiceRequest = super().save(commit=False)
        obj.status = "pending"
        lat, lng = self.CITY_GEO.get(self.cleaned_data["city"], (24.7136, 46.6753))
        # انحراف عشوائي خفيف ~ 0.05 درجة
        obj.lat = lat + (random.random() - 0.5) * 0.05
        obj.lng = lng + (random.random() - 0.5) * 0.05
        if commit:
            obj.save()
        return obj
