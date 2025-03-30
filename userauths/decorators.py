from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def vendor_required(view_func):
    """
    Decorador que verifica si el usuario es un Vendor (Proveedor).
    Redirige a una página de acceso denegado si no lo es.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.user_type == "Vendor":
                return view_func(request, *args, **kwargs)
        
        messages.error(request, "Acceso denegado. Esta área está reservada para proveedores.")
        return redirect('userauths:access_denied')
    return _wrapped_view

def customer_required(view_func):
    """
    Decorador que verifica si el usuario es un Customer (Cliente).
    Redirige a una página de acceso denegado si no lo es.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.user_type == "Customer":
                return view_func(request, *args, **kwargs)
        
        messages.error(request, "Acceso denegado. Esta área está reservada para clientes.")
        return redirect('userauths:access_denied')
    return _wrapped_view