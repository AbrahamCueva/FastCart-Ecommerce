from django import forms
from .models import BlogComment, MensajeContacto

class FormularioContacto(forms.ModelForm):
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'telefono', 'asunto', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escribe tu mensaje aquí...', 'rows': 5}),
        }
        
class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ["author", "email", "comment"]
        widgets = {
            "author": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo Electrónico"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "placeholder": "Escribe tu comentario...", "rows": 4}),
        }