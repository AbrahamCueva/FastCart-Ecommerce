from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store import models as store_models
from vendor import models as vendor_models
from django.db.models.functions import TruncMonth
from django.db import models
from plugin.paginate_queryset import paginate_queryset
from django.contrib import messages
from django.contrib.auth.hashers import check_password

def get_monthly_sales():
    monthly_sales = (
        store_models.OrderItem.objects.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(order_count=models.Count("id"))
        .order_by("month")
    )
    return monthly_sales

@login_required
def dashboard(request):
    products = store_models.Product.objects.filter(vendor=request.user)
    orders = store_models.Order.objects.filter(vendors=request.user)
    revenue = store_models.OrderItem.objects.filter(vendor=request.user).aggregate(total=models.Sum("total"))['total']
    notis = vendor_models.Notifications.objects.filter(user=request.user, seen=False)
    reviews = store_models.Review.objects.filter(product__vendor=request.user) 
    rating = store_models.Review.objects.filter(product__vendor=request.user).aggregate(avg=models.Avg("rating"))['avg']
    monthly_sales = get_monthly_sales()
    
    context = {
        "products": products,
        "orders": orders,
        "revenue": revenue,
        "notis": notis,
        "reviews": reviews,
        "rating": rating,
    }
    
    return render(request, "vendor/dashboard.html", context)
    
@login_required
def products(request):
    products_list = store_models.Product.objects.filter(vendor=request.user)
    products = paginate_queryset(request, products_list, 10)
    context = {
        "products": products,
        "products_list": products_list,
    }
    return render(request, "vendor/products.html", context)

@login_required
def orders(request):
    orders_list = store_models.Order.objects.filter(vendors=request.user, payment_status="Paid")
    orders = paginate_queryset(request, orders_list, 10)
    context = {
        "orders_list": orders_list,
        "orders": orders,
    }
    return render(request, "vendor/orders.html", context)

@login_required
def order_detail(request, order_id):
    order = store_models.Order.objects.get(vendors=request.user, order_id=order_id, payment_status="Paid")
    context = {
        "order": order,
    }
    return render(request, "vendor/order_detail.html", context)

@login_required
def order_item_detail(request, order_id, item_id):
    order = store_models.Order.objects.get(vendors=request.user, order_id=order_id, payment_status="Paid")
    item = store_models.OrderItem.objects.get(item_id=item_id, order=order)
    context = {
        "order": order,
        "item": item,
    }
    return render(request, "vendor/order_item_detail.html", context)

@login_required
def update_order_status(request, order_id):
    order = store_models.Order.objects.get(vendors=request.user, order_id=order_id, payment_status="Paid")
    if request.method == "POST":
        order_status = request.POST.get("order_status")
        order.order_status = order_status
        order.save()
        
        messages.success(request, "Estado de pedido actualizado")
        return redirect("vendor:order_detail", order.order_id)
    return redirect("vendor:order_detail", order.order_id)

@login_required
def update_order_item_status(request, order_id, item_id):
    order = store_models.Order.objects.get(vendors=request.user, order_id=order_id, payment_status="Paid")
    item = store_models.OrderItem.objects.get(item_id=item_id, order=order)
    if request.method == "POST":
        order_status = request.POST.get("order_status")
        shipping_service = request.POST.get("shipping_service")
        tracking_id = request.POST.get("tracking_id")
        
        item.order_status = order_status
        item.shipping_service = shipping_service
        item.tracking_id = tracking_id
        item.save()
        
        messages.success(request, "Estado producto en el pedido actualizado")
        return redirect("vendor:order_item_detail", order.order_id, item.item_id)
    return redirect("vendor:order_item_detail", order.order_id, item.item_id)

@login_required
def coupons(request):
    coupons_list = store_models.Coupon.objects.filter(vendor=request.user)
    coupons = paginate_queryset(request, coupons_list, 10)
    context = {
        "coupons": coupons,
        "coupons_list": coupons_list,
    }
    return render(request, "vendor/coupons.html", context)

@login_required
def update_coupon(request, id):
    coupon = store_models.Coupon.objects.get(vendor=request.user, id=id)
    if request.method == "POST":
        code = request.POST.get("coupon_code")
        coupon.code = code
        coupon.save()
    messages.success(request, "Cupón actualizado")
    return redirect("vendor:coupons")

@login_required
def delete_coupon(request, id):
    coupon = store_models.Coupon.objects.get(vendor=request.user, id=id)
    coupon.delete()
    messages.success(request, "Cupón eliminado")
    return redirect("vendor:coupons")

@login_required
def coupon_create(request):
    if request.method == "POST":
        code = request.POST.get("coupon_code")
        discount = request.POST.get("discount")
        store_models.Coupon.objects.create(vendor=request.user, code=code, discount=discount)
    messages.success(request, "Cupón creado")
    return redirect("vendor:coupons")

@login_required
def reviews(request):
    reviews_list = store_models.Review.objects.filter(product__vendor=request.user)
    reviews = paginate_queryset(request, reviews_list, 10)
    rating = request.GET.get("rating")
    date = request.GET.get("date")
    
    if rating:
        reviews = reviews.filter(rating=rating)
    
    if date:
        reviews = reviews.order_by(date)
        
    context = {
        "reviews": reviews,
        "reviews_list": reviews_list,
    }
    return render(request, "vendor/reviews.html", context)

@login_required
def update_repply(request, id):
    review = store_models.Review.objects.get(id=id)
    
    if request.method == "POST":
        repply = request.POST.get("repply")
        review.repply = repply
        review.save()
        
    messages.success(request, "Respuesta agregada")
    return redirect("vendor:reviews")

@login_required
def notis(request):
    notis_list = vendor_models.Notifications.objects.filter(user=request.user, seen=False)
    notis = paginate_queryset(request, notis_list, 1)
    context = {
        "notis": notis,
    }
    return render(request, "vendor/notis.html", context)

@login_required
def mark_noti_seen(request, id):
    noti = vendor_models.Notifications.objects.get(user=request.user, id=id)
    noti.seen = True
    noti.save()
    messages.success(request, "Notificacion vista")
    return redirect("vendor:notis")

@login_required
def profile(request):
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
        return redirect("vendor:profile")
    context = {
        "profile": profile
    }
    return render(request, "vendor/profile.html", context)

@login_required
def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_new_password = request.POST.get("confirm_new_password")

        if confirm_new_password != new_password:
            messages.error(request, "La nueva contraseña y confirmar contraseña no coinciden")
            return redirect("vendor:change_password")
        if check_password(old_password, request.user.password):
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Contraseña cambiada exitosamente")
            return redirect("vendor:profile")
        else :
            messages.error(request, "La contraseña antigua es incorrecta")
            return redirect("vendor:change_password")
    return render(request, "vendor/change_password.html")