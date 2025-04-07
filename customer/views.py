from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import models
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from plugin.paginate_queryset import paginate_queryset
from store import models as store_models
from customer import models as customer_models
from userauths.decorators import customer_required

@login_required
def dashboard(request):
    orders = store_models.Order.objects.filter(customer=request.user)
    total_spent = store_models.Order.objects.filter(customer=request.user).aggregate(total = models.Sum("total"))["total"]
    notis = customer_models.Notifications.objects.filter(user=request.user, seen=False)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "orders": orders,
        "total_spent": total_spent,
        "notis": notis,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/dashboard.html", context)

@login_required
def orders(request):
    orders_list = store_models.Order.objects.filter(customer=request.user)
    orders = paginate_queryset(request, orders_list, 10)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "orders": orders,
        "orders_list": orders_list,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/orders.html", context)

@login_required
def order_detail(request, order_id):
    order = store_models.Order.objects.get(customer=request.user, order_id=order_id)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "order": order,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/order_detail.html", context)

@login_required
def order_item_detail(request, order_id, item_id):
    order = store_models.Order.objects.get(customer=request.user, order_id=order_id)
    item = store_models.OrderItem.objects.get(order=order, item_id=item_id)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "order": order,
        "item": item,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/order_item_detail.html", context)

@login_required
def wishlist(request):
    wishlist_list = customer_models.Wishlist.objects.filter(user=request.user)
    wishlist = paginate_queryset(request, wishlist_list, 10)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "wishlist_list": wishlist_list,
        "wishlist": wishlist,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/wishlist.html", context)

@login_required
def remove_from_wishlist(request, id):
    wishlist = customer_models.Wishlist.objects.get(user=request.user, id=id)
    wishlist.delete()
    messages.success(request, "Producto eliminado de favoritos")
    return redirect("customer:wishlist")

def add_to_whislist(request, id):
    if request.user.is_authenticated:
        product = store_models.Product.objects.filter(id=id).first()
        wishlist_exists = customer_models.Wishlist.objects.filter(product=product, user=request.user).first()
        if not wishlist_exists:
            customer_models.Wishlist.objects.create(user=request.user, product=product)
        wishlist = customer_models.Wishlist.objects.filter(user=request.user)
        return JsonResponse({"message": "Producto agregado a favoritos", "wishlist_count": wishlist.count()})
    else:
        return JsonResponse({"message": "No estás logueado", "wishlist_count": "0"})
        
@login_required
def notis(request):
    notis_list = customer_models.Notifications.objects.filter(user=request.user, seen=False)
    notis = paginate_queryset(request, notis_list, 10)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "notis": notis,
        "notis_list": notis_list,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/notis.html", context)

@login_required
def mark_noti_seen(request, id):
    noti = customer_models.Notifications.objects.get(user=request.user, id=id)
    noti.seen = True
    noti.save()
    messages.success(request, "Notificacion vista")
    return redirect("customer:notis")

@login_required
def addresses(request):
    addresses = customer_models.Address.objects.filter(user=request.user)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "addresses": addresses,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/addresses.html", context)

@login_required
def address_detail(request, id):
    address = customer_models.Address.objects.get(user=request.user, id=id)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        country = request.POST.get("country")
        city = request.POST.get("city")
        state = request.POST.get("state")
        address_location = request.POST.get("address")
        zip_code = request.POST.get("zip_code")
        
        address.full_name = full_name
        address.mobile = mobile
        address.email = email
        address.country = country
        address.city = city
        address.state = state
        address.address = address_location
        address.zip_code = zip_code
        address.save()
        
        messages.success(request, "Dirección actualizada")
        return redirect("customer:address_detail", address.id)
    context = {
        "address": address,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/address_detail.html", context)

@login_required
def address_create(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        email = request.POST.get("email")
        country = request.POST.get("country")
        city = request.POST.get("city")
        state = request.POST.get("state")
        address = request.POST.get("address")
        zip_code = request.POST.get("zip_code")
        
        customer_models.Address.objects.create(
            user=request.user,
            full_name=full_name,
            mobile=mobile,
            email=email,
            country=country,
            city=city,
            state=state,
            address=address,
            zip_code=zip_code,
        )
        messages.success(request, "Dirección creada")
        return redirect("customer:addresses")
    context = {
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/address_create.html", context)

@login_required
def delete_addresses(request, id):
    address = customer_models.Address.objects.get(user=request.user, id=id)
    address.delete()
    messages.success(request, "Dirección eliminada")
    return redirect("customer:addresses")

@login_required
def profile(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    profile = request.user.profile
    if request.method == "POST":
        image = request.FILES.get("image")
        full_name = request.POST.get("full_name")
        mobile = request.POST.get("mobile")
        
        if image != None:
            profile.image = image
            
        profile.full_name = full_name
        profile.mobile = mobile
        
        request.user.save()
        profile.save()
        
        messages.success(request, "Perfil actualizado exitosamente")
        return redirect("customer:profile")
    context = {
        "settings": settings,
        "categories": categories,
        "profile": profile
    }
    return render(request, "customer/profile.html", context)

@login_required
def change_password(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        if confirm_new_password != new_password:
            messages.error(request, "La nueva contraseña y confirmar contraseña no coinciden")
            return redirect("customer:change_password")
        if check_password(old_password, request.user.password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Contraseña cambiada exitosamente")
            return redirect("customer:profile")
        else :
            messages.error(request, "La contraseña antigua es incorrecta")
            return redirect("customer:change_password")
    context = {
        "settings": settings,
        "categories": categories,
    }
    return render(request, "customer/change_password.html", context)

