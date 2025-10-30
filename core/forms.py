# core/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

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

class BaseSignupForm(forms.Form):
    username = forms.CharField(label="اسم المستخدم", max_length=150)
    password1 = forms.CharField(label="كلمة المرور", widget=forms.PasswordInput)
    password2 = forms.CharField(label="تأكيد كلمة المرور", widget=forms.PasswordInput)

    name = forms.CharField(label="الاسم الكامل", max_length=120)
    city = forms.ChoiceField(label="المدينة", choices=CITY_CHOICES)

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
            # يفعل محققات Django القياسية (الطول/التعقيد)
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


class OrganizationSignupForm(BaseSignupForm):
    # لا مهارات للجهة في الـMVP
    pass
