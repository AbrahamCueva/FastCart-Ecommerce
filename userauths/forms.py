from django import forms
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from userauths.models import User

USER_TYPE = (
    ("Vendor", "Vendedor"),
    ("Customer", "Cliente"),
)

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Nombres y apellidos'}), required=True)
    mobile = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Número de teléfono'}), required=True)
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Correo electrónico'}), required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Ingresa tu contraseña'}), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Confirma tu contraseña'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    user_type = forms.ChoiceField(choices=USER_TYPE, widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['full_name', 'mobile', 'email', 'password1', 'password2', 'captcha', 'user_type']

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Correo electrónico'}), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Ingresa tu contraseña'}), required=True)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ['email', 'password', 'captcha']
