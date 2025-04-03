from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from plugin.service_fee import calculate_service_fee
from store import models as store_models
from django.http import JsonResponse
from decimal import Decimal
from customer import models as customer_models
from vendor import models as vendor_models
from django.db.models import Q, Avg, Sum
from django.contrib import messages
from plugin.tax_calculation import tax_calculation
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from plugin.exchange_rate import convert_usd_inr, convert_usd_to_kobo, convert_usd_to_ngn
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from plugin.paginate_queryset import paginate_queryset
from .forms import BlogCommentForm, FormularioContacto
from django.views.decorators.csrf import csrf_exempt
from .models import Subscriber
import requests
import stripe
import random
import json

stripe.api_key = settings.STTRIPE_SECRET_KEY

@csrf_exempt
def subscribe(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if not email:
                return JsonResponse({"error": "El correo electrónico es obligatorio."}, status=400)

            subscriber, created = Subscriber.objects.get_or_create(email=email)

            if created:
                return JsonResponse({"message": "¡Te has suscrito correctamente!"}, status=201)
            else:
                return JsonResponse({"message": "¡Este correo ya está suscrito!"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Formato JSON inválido."}, status=400)

    return JsonResponse({"error": "Método de solicitud no permitido."}, status=405)

def search_view(request):
    query = request.GET.get("q", "").strip()  # Elimina espacios al principio y al final
    category_query = request.GET.get("category", "").strip()
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()

    # Validación: Si el término de búsqueda está vacío, redirigimos o mostramos un mensaje
    if not query:
        # Puedes redirigir a una página de inicio o mostrar un mensaje específico
        # En este caso, redirigimos a la página principal
        return redirect('store:index')

    products = store_models.Product.objects.filter(status="Published")

    if query:
        products = products.filter(Q(name__icontains=query))

    if category_query:
        products = products.filter(category__id=category_query)

    context = {
        "products": products,
        "query": query,
        "category_query": category_query,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "store/search_results.html", context)
    
def about_us(request):
    about = store_models.AboutUs.objects.first()
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "settings": settings,
        "categories": categories,
        "about": about,
    }
    return render(request, 'store/about-us.html', context)

def index(request):
    products = list(store_models.Product.objects.filter(status="Published"))  # Convertir a lista
    random.shuffle(products)  # Mezclar aleatoriamente
    products = products[:10]  # Seleccionar solo 10 productos aleatorios

    categories = store_models.Category.objects.all()[:5]
    sliders = store_models.Slider.objects.filter(status="Active").order_by("-created_at")
    settings = store_models.StoreSettings.objects.first()

    context = {
        "products": products,
        "categories": categories,
        "sliders": sliders,
        "settings": settings,
    }
    return render(request, "store/index.html", context)

def category_list(request):
    settings = store_models.StoreSettings.objects.first()
    categories_list = store_models.Category.objects.all() 
    categories = paginate_queryset(request, categories_list, 12)
    for category in categories:
        category.product_count = store_models.Product.objects.filter(category=category).count() 
    context = {
        "settings": settings,
        "categories": categories,
        "categories_list": categories_list,
    }
    return render(request, "store/category_list.html", context)

def category_detail(request, slug):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all() 
    category = get_object_or_404(store_models.Category, slug=slug)  
    products_list = store_models.Product.objects.filter(category=category)  
    products = paginate_queryset(request, products_list, 15)
    
    context = {
        "category": category,
        "products": products,
        "settings": settings,
        "products_list": products_list,
        "categories": categories,
    }
    return render(request, "store/category_detail.html", context)

def product_detail(request, slug):
    product = store_models.Product.objects.get(status="Published", slug=slug)
    related_products = store_models.Product.objects.filter(category=product.category, status="Published").exclude(id=product.id) 
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    product_stock_range = range(1, product.stock + 1)
    context = {
        "product": product,
        "related_products": related_products,
        "product_stock_range": product_stock_range,
        "settings": settings,
        "categories": categories,
        'page_title': f"{product.name} - {settings.store_name}"
    }
    return render(request, "store/product_detail.html", context)

def blog(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    posts_list = store_models.BlogPost.objects.filter(status="Published")
    tags = store_models.Tag.objects.all()
    posts = paginate_queryset(request, posts_list, 10)
    context = {
        "settings": settings,
        "categories": categories,
        "posts": posts,
        "posts_list": posts_list,
        "tags": tags,
    }
    return render(request, "store/blog.html", context=context)

def blog_detail(request, slug):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    category_post = store_models.CategoryPost.objects.first()
    post = get_object_or_404(store_models.BlogPost, slug=slug, status="Published")
    comments = post.comments.all().order_by("-created_at")

    tags = post.tags.all() 

    if request.method == "POST":
        form = BlogCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            messages.success(request, "Tu comentario ha sido enviado correctamente.")
            return redirect("store:blog_detail", slug=slug) 
    else:
        form = BlogCommentForm()

    context = {
        "settings": settings,
        "categories": categories,
        "post": post,
        "category_post": category_post,
        "comments": comments,
        "form": form,
        "tags": tags, 
    }
    return render(request, "store/blog_detail.html", context)

def add_to_cart(request):
    id = request.GET.get("id")
    qty = request.GET.get("qty")
    color = request.GET.get("color")
    size = request.GET.get("size")
    cart_id = request.GET.get("cart_id")
    print("color ===", color)
    print("size ===", size)
    request.session['cart_id'] = cart_id
    if not id or not qty or not cart_id:
        return JsonResponse({"error": "No id, qty or cart_id provided."}, status=400)
    
    try:
        product = store_models.Product.objects.get(id=id, status="Published")
    except store_models.Product.DoesNotExist:
        return JsonResponse({"error": "Producto no encontrado."}, status=404)
    
    existing_cart_items = store_models.Cart.objects.filter(cart_id=cart_id, product=product).first()
    
    if int(qty) > product.stock:
        return JsonResponse({"error": "La cantidad supera al stock registrado."}, status=404)

    if not existing_cart_items:
        cart = store_models.Cart()
        cart.product = product
        cart.qty = qty
        cart.price = product.price
        cart.color = color
        cart.size = size
        cart.sub_total = Decimal(product.price) * Decimal(qty)
        cart.shipping = Decimal(product.shipping) * Decimal(qty)
        cart.total = cart.sub_total + cart.shipping
        cart.user = request.user if request.user.is_authenticated else None
        cart.cart_id = cart_id
        cart.save()
        message = "Producto agregado al cesto"
    else :
        existing_cart_items.product = product
        existing_cart_items.qty = qty
        existing_cart_items.price = product.price
        existing_cart_items.color = color
        existing_cart_items.size = size
        existing_cart_items.sub_total = Decimal(product.price) * Decimal(qty)
        existing_cart_items.shipping = Decimal(product.shipping) * Decimal(qty)
        existing_cart_items.total = existing_cart_items.sub_total + existing_cart_items.shipping
        existing_cart_items.user = request.user if request.user.is_authenticated else None
        existing_cart_items.cart_id = cart_id
        existing_cart_items.save()
        message = "Cesto actualizado"
    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(cart_id=cart_id))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(cart_id=cart_id)).aggregate(sub_total=Sum("sub_total"))['sub_total']
    return JsonResponse(
        { 
            "message": message,
            "total_cart_items": total_cart_items.count(),
            "cart_sub_total": "{:,.2f}" . format(cart_sub_total),
            "item_sub_total": "{:,.2f}" . format(existing_cart_items.sub_total) if existing_cart_items else "{:,.2f}" . format(cart.sub_total)
        },
    )
    
def cart(request):
    if "cart_id" in request.session:
        cart_id = request.session['cart_id']
    else :
        cart_id = None
        
    items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id))
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(sub_total = Sum("sub_total"))['sub_total']
    try:
        addresses = customer_models.Address.objects.filter(user=request.user)
    except:
        addresses = None
        
    if not items:
        messages.warning(request, "El cesto está vacío")
        return redirect("store:index")

    context = {
        "items": items,
        "cart_sub_total": cart_sub_total,
        "addresses": addresses,
        "settings": settings,
        "categories": categories,
    }
    
    return render(request, "store/cart.html", context)
    
def delete_cart_item(request):
    id = request.GET.get("id")
    item_id = request.GET.get("item_id")
    cart_id = request.GET.get("cart_id")
    
    if not id and not item_id and not cart_id:
        return JsonResponse(
            {"error": "Id del producto no encontrado"}, status=400
        )
        
    try:
        product = store_models.Product.objects.get(status="Published", id=id)
    except store_models.Product.DoesNotExist:
        return JsonResponse(
            {"error": "Producto no encontrado."}, status=404
        )
        
    item = store_models.Cart.objects.get(product=product, id=item_id)
    item.delete()
    total_cart_items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user))
    cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user)).aggregate(sub_total = Sum("sub_total"))['sub_total']
    return JsonResponse({
        "message": "Producto eliminado",
        "total_cart_items": total_cart_items.count(),
        "cart_sub_total": "{:,.2f}".format(cart_sub_total) if cart_sub_total else 0.00
    })
    
def create_order(request):
    if request.method == "POST":
        address_id = request.POST.get("address")
        if not address_id:
            messages.warning(request, "Porfavor selecciona una dirección para continuar")
            return redirect("store:cart")
        
        address = customer_models.Address.objects.filter(user=request.user, id=address_id).first()
        if 'cart_id' in request.session:
            cart_id = request.session['cart_id']
        else:
            cart_id = None
        items = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)) 
        cart_sub_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(sub_total = Sum("sub_total"))['sub_total']
        cart_shipping_total = store_models.Cart.objects.filter(Q(cart_id=cart_id) | Q(user=request.user) if request.user.is_authenticated else Q(cart_id=cart_id)).aggregate(shipping = Sum("shipping"))['shipping']
        order = store_models.Order()
        order.sub_total = cart_sub_total
        order.customer = request.user 
        order.address = address
        order.shipping = cart_shipping_total
        order.tax = tax_calculation(address.country, cart_sub_total)
        order.total = order.sub_total + order.shipping + Decimal(order.tax)
        order.service_fee = calculate_service_fee(order.total)
        order.total += order.service_fee
        order.initial_total = order.total
        order.save()
        for i in items:
            store_models.OrderItem.objects.create(
                order=order,
                product=i.product,
                qty=i.qty,
                color=i.color,
                size=i.size,
                price=i.price,
                sub_total=i.sub_total,
                shipping=i.shipping,
                tax=tax_calculation(address.country, i.sub_total),
                total=i.total,
                initial_total=i.total,
                vendor=i.product.vendor
            )
            order.vendors.add(i.product.vendor)
    return redirect("store:checkout", order.order_id)

def checkout(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    amount_in_inr = convert_usd_inr(order.total)
    amount_in_kobo = convert_usd_to_kobo(order.total)
    amount_in_ngn = convert_usd_to_ngn(order.total)
    order_total_paypal = str(order.total).replace(',', '.')
    context = {
        "order": order,
        "amount_in_inr": amount_in_inr,
        "amount_in_kobo": amount_in_kobo,
        "amount_in_ngn": amount_in_ngn,
        "order": order,
        "paypal_client_id": settings.PAYPPAL_CLIENT_ID,
        "order_total_paypal": order_total_paypal, 
        "stripe_public_key": settings.STTRIPE_PUBLIC_KEY,
        "paystack_public_key": settings.PAYSTTACK_PUBLIC_KEY,
        "flutterwavee_public_key": settings.FLUTTERWAVEE_PUBLIC_KEY,
        "settings": settings,
        "categories": categories,
    }
    return render(request, "store/checkout.html", context)
        
def coupon_apply(request, order_id):
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        order_items = store_models.OrderItem.objects.filter(order=order)
    except store_models.Order.DoesNotExist:
        return redirect("store:cart")
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        if not coupon_code:
            messages.error(request, "No se ha introducido ningún cupón")
            return redirect("store:checkout", order.order_id)
        try:
            coupon = store_models.Coupon.objects.get(code=coupon_code)
        except store_models.Coupon.DoesNotExist:
            messages.error(request, "El cupón introducido no existe")
            return redirect("store:checkout", order.order_id)
        if coupon in order.coupons.all():
            messages.error(request, "cupón ya activado")
            return redirect("store:checkout", order.order_id)
        else:
            total_discount = 0
            for item in order_items:
                if coupon.vendor == item.product.vendor and coupon not in item.coupon.all():
                    item_discount = item.total * coupon.discount / 100
                    total_discount += item_discount
                    item.coupon.add(coupon)
                    item.total -= item_discount
                    item.saved += item_discount
                    item.save()
            if total_discount > 0:
                order.coupons.add(coupon)
                order.total -= total_discount
                order.sub_total -= total_discount
                order.saved += total_discount
                order.save()
        messages.success(request, f"Cupón '{coupon.code}' aplicado correctamente")
        return redirect("store:checkout", order.order_id)

def clear_cart_items(request):
    try:
        cart_id = request.session['cart_id']
        store_models.Cart.objects.filter(cart_id=cart_id).delete()
    except:
        pass
    return

def get_paypal_access_token():
    token_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {'grant_type': 'client_credentials'}
    auth = (settings.PAYPPAL_CLIENT_ID, settings.PAYPPAL_SECRET_ID)
    response = requests.post(token_url, data=data, auth=auth)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"No se pudo obtener el token de acceso de Paypal. Código de estado: {response.status_code}")
    
def paypal_payment_verify(request, order_id):
    try:
        order = store_models.Order.objects.get(order_id=order_id)
        transaction_id = request.GET.get("transaction_id")
        frontend_status = request.GET.get("status")
        
        print(f"1. Transaction ID recibido: {transaction_id}")
        print(f"2. Estado reportado por frontend: {frontend_status}")
        
        if frontend_status in ["COMPLETED", "APPROVED"]:
            print(f"3. Estado válido reportado por frontend: {frontend_status}")
            order.payment_status = "Paid"
            order.payment_method = "Paypal"
            order.payment_id = transaction_id
            order.save()
            clear_cart_items(request)
            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
        
        if not transaction_id:
            print("3. No se recibió transaction_id")
            return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
            
        paypal_api_url = f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{transaction_id}"
        
        access_token = get_paypal_access_token()
        print(f"4. Token de acceso obtenido: {access_token[:10]}...") 
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {access_token}",
        }
        
        print(f"5. Consultando API de PayPal para transacción: {transaction_id}")
        response = requests.get(paypal_api_url, headers=headers)
        print(f"6. Código de respuesta API PayPal: {response.status_code}")
        
        if response.status_code == 200:
            paypal_order_data = response.json()
            print(f"7. Datos de la orden PayPal: {paypal_order_data}")
            paypal_payment_status = paypal_order_data.get('status')
            print(f"8. Estado del pago según PayPal API: {paypal_payment_status}")
            
            purchase_units = paypal_order_data.get('purchase_units', [])
            if purchase_units and 'payments' in purchase_units[0]:
                captures = purchase_units[0]['payments'].get('captures', [])
                if captures and captures[0].get('status') == "COMPLETED":
                    print("9. ¡Captura completada encontrada!")
                    paypal_payment_status = "COMPLETED"
            
            if paypal_payment_status in ["COMPLETED", "APPROVED"]:
                print(f"10. Estado válido, actualizando pedido a pagado")
                order.payment_status = "Paid"
                order.payment_method = "Paypal"
                order.payment_id = transaction_id
                order.save()
                clear_cart_items(request)
                return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
            else:
                print(f"10. Estado no válido: {paypal_payment_status}")
        else:
            print(f"7. Error en respuesta PayPal: {response.status_code}")
            print(f"8. Texto de respuesta: {response.text}")
        
        print("Redirigiendo a estado de pago fallido")
        return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
    except Exception as e:
        print(f"Error en la verificación del pago: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")
    
def payment_status(request, order_id):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    order = store_models.Order.objects.get(order_id=order_id)
    payment_status = request.GET.get("payment_status")
    context = {
        "settings": settings,
        "categories": categories,
        "order": order,
        "payment_status": payment_status
    }
    return render(request, "store/payment_status.html", context)
    
@csrf_exempt
def stripe_payment(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    stripe.api_key = settings.STTRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_email = order.address.email,
        payment_method_types = ['card'],
        line_items = [
            {
                'price_data': {
                    'currency': "PEN",
                    'product_data': {
                        'name': order.address.full_name
                    },
                    'unit_amount': int(order.total * 100)
                },
                'quantity': 1
            }
        ],
        mode = 'payment',
        success_url = request.build_absolute_uri(reverse("store:stripe_payment_verify", args=[order.order_id])) + "?session_id={CHECKOUT_SESSION_ID}" + "&payment_method=Stripe",
        cancel_url = request.build_absolute_uri(reverse("store:stripe_payment_verify", args=[order.order_id])),
    )
    print("checkout_session: ", checkout_session),
    return JsonResponse({"sessionId": checkout_session.id})

def stripe_payment_verify(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    stripe.api_key = settings.STTRIPE_SECRET_KEY
    session_id = request.GET.get("session_id")
    session = stripe.checkout.Session.retrieve(session_id)
    if session.payment_status == "paid":
        if order.payment_status == "Processing":
            order.payment_status = "Paid"
            order.payment_method = "Stripe"
            order.save()
            clear_cart_items(request)
            
            # Send Email to Customer
            customer_merge_data = {
                'order': order,
                'order_items': order.order_items()
            }
            subject = f"Nuevo pedido"
            text_body = render_to_string("mail/order/customer/customer_new_order.txt", customer_merge_data)
            html_body = render_to_string("mail/order/customer/customer_new_order.html", customer_merge_data)
            msg = EmailMultiAlternatives(
                subject=subject, from_email=settings.FROM_EMAIL,
                to=[order.address.email], body=text_body
            )
            msg.attach_alternative(html_body, 'text/html')
            msg.send()
            customer_models.Notifications.objects.create(type="New Order", user=request.user)
            for item in order.order_items():
                vendor_merge_data = {
                    'item': item,
                    'order': order,
                }
                subject = f"Nueva venta"
                text_body = render_to_string("mail/order/vendor/vendor_new_order.txt", vendor_merge_data)
                html_body = render_to_string("mail/order/vendor/vendor_new_order.html", vendor_merge_data)
                msg = EmailMultiAlternatives(
                    subject=subject, from_email=settings.FROM_EMAIL,
                    to=[item.vendor.email], body=text_body
                )
                msg.attach_alternative(html_body, 'text/html')
                msg.send()
                vendor_models.Notifications.objects.create(type="New Order", user=item.vendor, order=item)
            
            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
    return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

def paystack_payment_verify(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    reference = request.GET.get("reference", "")
    if reference:
        headers = {
            "Authorization": f"Bearer {settings.PAYSTTACK_PRIVATE_KEY}",
            "Content-Type": "Application/json"
        }
        response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        response_data = response.json()
        if response_data['status']:
            if response_data['data']['status'] == 'success':
                if order.payment_status == "Processing":
                    order.payment_status = "Paid"
                    order.payment_method = "Paystack"
                    order.save()
                    clear_cart_items(request)
                    
                    # Send Email to Customer
                    
                    # Send InApp Notification
                    
                    #Send email to vendor
                    
                    return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
        return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

def flutterwave_payment_callback(request, order_id):
    order = store_models.Order.objects.get(order_id=order_id)
    tx_ref = request.GET.get("tx_ref", "")
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVEE_PRIVATE_KEY}",
        "Content-Type": "Application/json"
    }
    response = requests.get(f"https://api.flutterwave.com/v3/transactions/verify_by_reference?tx_ref={tx_ref}", headers=headers)
    response_data = response.json()
    if response_data['data']['status'] == "successful":
        if order.payment_status == "Processing":
            order.payment_status = "Paid"
            order.payment_method = "Flutterwave"
            order.save()
            clear_cart_items(request)
                    
            return redirect(f"/payment_status/{order.order_id}/?payment_status=paid")
    return redirect(f"/payment_status/{order.order_id}/?payment_status=failed")

@login_required
def add_review(request, product_id):
    product = get_object_or_404(store_models.Product, id=product_id)

    if request.method == "POST":
        review_text = request.POST.get("review")
        rating = request.POST.get("rating")

        if not review_text:
            messages.error(request, "Por favor, ingresa tu consulta o comentario.")
            return redirect("store:product_detail", slug=product.slug)

        if not rating:
            messages.error(request, "Por favor, selecciona una calificación.")
            return redirect("store:product_detail", slug=product.slug)

        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                messages.error(request, "La calificación debe estar entre 1 y 5.")
                return redirect("store:product_detail", slug=product.slug)
        except ValueError:
            messages.error(request, "La calificación debe ser un número.")
            return redirect("store:product_detail", slug=product.slug)

        store_models.Review.objects.create(
            user=request.user,
            product=product,
            review=review_text,
            rating=rating,
            active=True 
        )
        messages.success(request, "Tu comentario ha sido enviado.")
        return redirect("store:product_detail", slug=product.slug)

    # Si no es POST, podrías renderizar un formulario de reseña (opcional)
    context = {
        'product': product,
    }
    return render(request, 'store/add_review_form.html', context)

def contacto(request):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    if request.method == "POST":
        form = FormularioContacto(request.POST)
        if form.is_valid():
            mensaje = form.save()

            # Enviar correo al administrador
            send_mail(
                subject=f"Nuevo Mensaje de Contacto: {mensaje.asunto}",
                message=f"Nombre: {mensaje.nombre}\n"
                        f"Correo: {mensaje.email}\n"
                        f"Teléfono: {mensaje.telefono}\n"
                        f"Mensaje:\n{mensaje.mensaje}",
                from_email="no-reply@tuempresa.com",
                recipient_list=["abrahamrico546@gmail.com"],  # Cambia esto al correo del administrador
                fail_silently=False,
            )

            messages.success(request, "Tu mensaje ha sido enviado correctamente. ¡Nos pondremos en contacto pronto!")
            return redirect("store:contacto")
    else:
        form = FormularioContacto()

    return render(request, "store/contacto.html", {"form": form, "settings": settings, "categories": categories})

def custom_404(request, exception):
    settings = store_models.StoreSettings.objects.first()
    categories = store_models.Category.objects.all()
    context = {
        "settings": settings,
        "categories": categories,
    }
    return render(request, "store/404.html", status=404, context=context)

def shop(request):
    products_list = store_models.Product.objects.filter(status="Published")
    categories = store_models.Category.objects.all()[:5]
    sliders = store_models.Slider.objects.filter(status="Active").order_by("-created_at")
    new_products = store_models.Product.objects.filter(status="Published").order_by("-id")[:3]
    settings = store_models.StoreSettings.objects.first()
    products = paginate_queryset(request, products_list, 20)
    context = {
        "products": products,
        "categories": categories,
        "sliders": sliders,
        "settings": settings,
        "products_list": products_list,
        "new_products": new_products,
    }
    return render(request, "store/shop.html", context)