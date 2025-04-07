from django.shortcuts import render, redirect
from django.contrib import messages
from userauths import forms as userauths_forms
from store import models as store_models
from vendor import models as vendor_models
from django.contrib.auth import authenticate, login, logout
from userauths import models as userauths_models

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib import messages
from django.shortcuts import render, redirect
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.forms import SetPasswordForm
from django.utils.encoding import force_bytes

def register_view(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    if request.user.is_authenticated:
        messages.warning(request, "Ya has iniciado sesión")
        return redirect("/")
    form = userauths_forms.UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        full_name = form.cleaned_data.get("full_name")
        email = form.cleaned_data.get("email")
        mobile = form.cleaned_data.get("mobile")
        password = form.cleaned_data.get("password1")
        user_type = form.cleaned_data.get("user_type")
        user = authenticate(email=email, password=password)
        login(request, user)
        messages.success(request, "Cuenta creada exitosamente")
        profile = userauths_models.Profile.objects.create(full_name=full_name, mobile=mobile, user=user)
        if user_type == "Vendor":
            vendor_models.Vendor.objects.create(user=user, store_name=full_name)
            profile.user_type = "Vendor"
        else:
            profile.user_type = "Customer"
        profile.save()
        next_url = request.GET.get("next", "store:index")
        return redirect(next_url)
    context = {
        "settings": settings,
        "categories": categories,
        "form": form,
    }
    return render(request, "userauths/sign-up.html", context)

def login_view(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    if request.user.is_authenticated:
        messages.warning(request, "Ya has iniciado sesión")
        return redirect("/")
    if request.method == "POST":
        form = userauths_forms.LoginForm(request.POST or None)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            captcha_verified = form.cleaned_data.get("captcha", False)
            if captcha_verified:
                try:
                    user_instance = userauths_models.User.objects.get(email=email, is_active=True)
                    user_authenticate = authenticate(request, email=email, password=password)
                    if user_instance is not None:
                        login(request, user_authenticate)
                        messages.success(request, "Ya has iniciado sesión")
                        next_url = request.GET.get("next", "store:index")
                        return redirect(next_url)
                    else:
                        messages.error(request, "El usuario y/o contraseña no existen")
                except:
                    messages.error(request, "El usuario no existe")
            else:
                messages.error(request, "Verificación de captcha fallida, intenta otra vez")
    else:
        form = userauths_forms.LoginForm()
    context = {
        "settings": settings,
        "categories": categories,
        "form": form,
    }
    return render(request, "userauths/sign-in.html", context)

def logout_view(request):
    if 'cart_id' in request.session:
        cart_id = request.session['cart_id']
    else:
        cart_id = None
    logout(request)
    request.session['cart_id'] = cart_id
    messages.success(request, "Has cerrado tu sesión")
    return redirect("userauths:sign-in")

def access_denied(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "settings": settings,
        "categories": categories,
    }
    """
    Vista que muestra un mensaje de acceso denegado cuando un usuario
    intenta acceder a una sección para la que no tiene permisos.
    """
    return render(request, 'userauths/access_denied.html', context)

def forgot_password_view(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()

    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = get_user_model().objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))  

            reset_url = request.build_absolute_uri(f'/user/reset-password/{uid}/{token}/')

            subject = "Recuperación de contraseña"
            message = render_to_string('userauths/mails/password_reset_email.html', {
                'reset_url': reset_url,
                'user': user,
            })
            send_mail(
                subject,
                '',  
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=message 
            )
            messages.success(request, "Te hemos enviado un enlace para restablecer tu contraseña")
        except get_user_model().DoesNotExist:
            messages.error(request, "El correo electrónico no está registrado")

    context = {
        "settings": settings,
        "categories": categories,
    }
    return render(request, "userauths/forgot-password.html", context)

from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib import messages
from store import models as store_models 

def reset_password_view(request, uidb64, token):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Tu contraseña ha sido restablecida con éxito")
                return redirect("userauths:sign-in")
            else:
                messages.error(request, "Hubo un error al restablecer la contraseña. Verifica los datos.")
        else:
            form = SetPasswordForm(user)
    else:
        messages.error(request, "El enlace de restablecimiento de contraseña es inválido o ha expirado.")
        return redirect("userauths:forgot-password")

    context = {
        "settings": settings,
        "categories": categories,
        "form": form,
    }
    return render(request, "userauths/reset-password.html", context)
