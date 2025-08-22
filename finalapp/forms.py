from django import forms
from .models import Member ,Complaint, Payment, Room, LeaseAgreement, News
from django.contrib.auth.models import User

class MemberForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('ชาย', 'ชาย'),
        ('หญิง', 'หญิง'),
    ]

    sex = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Member
        fields = ['profile_picture', 'fullname', 'email', 'phone', 'address', 'sex', 'birthday']
        widgets = {
            'birthday': forms.DateInput(attrs={'type': 'date'}),
        }

class ComplaintForm(forms.ModelForm):
    room = forms.ModelChoiceField(queryset=Room.objects.all(), required=True)

    class Meta:
        model = Complaint
        fields = ['room', 'description']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['slip']  # ฟิลด์ที่สามารถอัปโหลดคือ 'slip'
        widgets = {
            'slip': forms.ClearableFileInput(attrs={'multiple': False}),
        }

class LeaseAgreementForm(forms.ModelForm):
    class Meta:
        model = LeaseAgreement
        fields = ['file']
    
class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }