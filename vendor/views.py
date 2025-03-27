from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store import models as store_models
from vendor import models as vendor_models
from django.db.models.functions import TruncMonth
from django.db import models
from plugin.paginate_queryset import paginate_queryset
from django.contrib import messages

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


