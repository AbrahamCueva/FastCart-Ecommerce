from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from store import models as store_models
from vendor import models as vendor_models
from django.db.models.functions import TruncMonth
from django.db import models
from plugin.paginate_queryset import paginate_queryset
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
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

@login_required
def create_product(request):
    categories = store_models.Category.objects.all()
    
    if request.method == "POST":
        image = request.FILES.get("image")
        name = request.POST.get("name")
        category_id = request.POST.get("category_id")
        description = request.POST.get("description")
        price = request.POST.get("price")
        shipping = request.POST.get("shipping")
        regular_price = request.POST.get("regular_price")
        stock = request.POST.get("stock")
        
        category = store_models.Category.objects.get(id=category_id)
        product = store_models.Product.objects.create(
            image = image,
            vendor = request.user,
            name = name,
            category = category,
            description = description,
            price = price,
            regular_price = regular_price,
            shipping = shipping,
            stock = stock,
        )
        return redirect("vendor:update_product", product.id)
    context = {
        "categories": categories,
    }
    return render(request, "vendor/create_product.html", context)

@login_required
def update_product(request, id):
    product = store_models.Product.objects.get(vendor=request.user, id=id)
    categories = store_models.Category.objects.all()

    if request.method == "POST":
        image = request.FILES.get("image")
        name = request.POST.get("name")
        category_id = request.POST.get("category_id")
        description = request.POST.get("description")
        regular_price = request.POST.get('regular_price').replace(',', '.')
        price = request.POST.get('price').replace(',', '.')
        shipping = request.POST.get('shipping').replace(',', '.')
        stock = request.POST.get("stock")
        category = store_models.Category.objects.get(id=category_id)
        
        product.name = name
        product.category = category
        product.description = description
        product.price = price
        product.shipping = shipping
        product.regular_price = regular_price
        product.stock = stock
        
        if image:
            product.image = image
        
        product.save()
        
        variant_ids = request.POST.getlist("variant_id[]")
        variant_titles = request.POST.getlist("variant_title[]")

        existing_variant_ids = set(store_models.Variant.objects.filter(product=product).values_list('id', flat=True))
        received_variant_ids = set(map(int, filter(None, variant_ids)))

        # Eliminar variantes que ya no están en el formulario
        variants_to_delete = existing_variant_ids - received_variant_ids
        store_models.Variant.objects.filter(id__in=variants_to_delete).delete()

        if variant_titles:
            for i in range(len(variant_titles)):
                variant_id = variant_ids[i] if i < len(variant_ids) else None
                variant_name = variant_titles[i]

                variant = None  # Inicializa variant fuera del bloque if

                if variant_id:
                    variant = store_models.Variant.objects.filter(id=variant_id).first()
                    if variant:
                        variant.name = variant_name
                        variant.save()
                    else:
                        # La variante existente no se encontró (esto debería ser raro)
                        pass  # O podrías loggear un error aquí
                else:
                    variant = store_models.Variant.objects.create(product=product, name=variant_name)

                # Manejo de ítems de variantes
                item_ids = request.POST.getlist(f"item_id_{i}[]")
                item_titles = request.POST.getlist(f"item_title_{i}[]")
                item_descriptions = request.POST.getlist(f"item_description_{i}[]")

                # Solo acceder a variant_items si variant no es None
                if variant:
                    existing_item_ids = set(variant.variant_items.values_list('id', flat=True))
                    received_item_ids = set(map(int, filter(None, item_ids)))

                    # Eliminar ítems no presentes
                    items_to_delete = existing_item_ids - received_item_ids
                    store_models.VariantItem.objects.filter(id__in=items_to_delete).delete()

                    if item_titles:
                        for j in range(len(item_titles)):
                            item_id = item_ids[j] if j < len(item_ids) else None
                            item_title = item_titles[j]
                            item_description = item_descriptions[j]

                            if item_id:
                                variant_item = store_models.VariantItem.objects.filter(id=item_id).first()
                                if variant_item:
                                    variant_item.title = item_title
                                    variant_item.content = item_description
                                    variant_item.save()
                            else:
                                store_models.VariantItem.objects.create(
                                    variant=variant,
                                    title=item_title,
                                    content=item_description,
                                )

        for file_key, image_file in request.FILES.items():
            if file_key.startswith("image_"):
                store_models.Gallery.objects.create(product=product, image=image_file)

        messages.success(request, "Producto actualizado")
        return redirect("vendor:update_product", product.id)

    context = {
        "product": product,
        "categories": categories,
        "variants": store_models.Variant.objects.filter(product=product),
        "gallery_images": store_models.Gallery.objects.filter(product=product),
    }

    return render(request, "vendor/update_product.html", context)

def delete_variants(request, product_id, variant_id):
    product = store_models.Product.objects.get(id=product_id)
    variants = store_models.Variant.objects.get(id=variant_id, product__vendor=request.user, product=product)
    variants.delete()
    return JsonResponse({"message": "Variante eliminada"})

def delete_variants_items(request, variant_id, item_id):
    variants = store_models.Variant.objects.get(id=variant_id)
    item = store_models.VariantItem.objects.get(variant=variants, id=item_id)
    item.delete()
    return JsonResponse({"message": "Artículo de variante eliminada"})

def delete_product_image(request, product_id, image_id):
    product = store_models.Product.objects.get(id=product_id)
    image = store_models.Gallery.objects.get(id=image_id, product=product)
    image.delete()
    return JsonResponse({"message": "Imágen de este producto ha sido eliminada"})

def delete_product(request, product_id):
    product = store_models.Product.objects.get(id=product_id)
    product.delete()
    return redirect("vendor:products")
