from django.shortcuts import render, redirect
from django.contrib import messages
from userauths import forms as userauths_forms
from vendor import models as vendor_models
from django.contrib.auth import authenticate, login, logout
from userauths import models as userauths_models

def register_view(request):
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
        "form": form,
    }
    return render(request, "userauths/sign-up.html", context)

def login_view(request):
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

# Añade esta función a tu archivo views.py existente

def access_denied(request):
    """
    Vista que muestra un mensaje de acceso denegado cuando un usuario
    intenta acceder a una sección para la que no tiene permisos.
    """
    return render(request, 'userauths/access_denied.html')

# Ejemplo de cómo usar los decoradores en tus vistas:
# from .decorators import vendor_required, customer_required
#
# @vendor_required
# def vendor_dashboard(request):
#     return render(request, 'vendor/dashboard.html')
#
# @customer_required
# def customer_dashboard(request):
#     return render(request, 'customer/dashboard.html')