from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

from userauths import models as user_models

import shortuuid

STATUS = (
    ("Published", "Publicado"),
    ("Draft", "Borrador"),
    ("Disabled", "Desactivado"),
)

PAYMENT_STATUS = (
    ("Paid", "Pagado"),
    ("Processing", "En proceso"),
    ("Failed", "Fallido"),
)

PAYMENT_METHOD = (
    ("Paypal", "Paypal"),
    ("Stripe", "Stripe"),
    ("Flutterwave", "Flutterwave"),
    ("Paystack", "Paystack"), 
)

ORDER_STATUS = (
    ("Pending", "Pendiente"),
    ("Processing", "En proceso"),
    ("Shipped", "Enviado"),
    ("Fullfiled", "Entregado"),
    ("Cancelled", "Cancelado"),
)

SHIPPING_SERVICE = (
    ("DHL", "DHL"),
    ("FedEx", "FedEx"),
    ("UPS", "UPS"),
    ("GIG Logistics", "GIG Logistics"),
)

RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)

class Category(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images", blank=True, null=True)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ["title"]
        
class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="images", blank=True, null=True)
    description = CKEditor5Field('Text', config_name='extends')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Precio de venta")
    regular_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Precio Regular")
    
    stock = models.PositiveIntegerField(default=0, null=True, blank=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, verbose_name="Costo de envío")
    
    status = models.CharField(choices=STATUS, max_length=50, default="Published")
    featured = models.BooleanField(default=False, verbose_name="Destacado")
    
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    
    sku = ShortUUIDField(unique=True, length=5, max_length=50, prefix="SKU", alphabet="1234567890")
    slug = models.SlugField(null=True, blank=True)
    
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Productos"
        
    def __str__(self):
        return self.name
    
    def average_rating(self):
        avg = Review.objects.filter(product=self).aggregate(avg_rating=models.Avg("rating"))["avg_rating"]
        return avg if avg is not None else 0
        
    def reviews(self):
        return Review.objects.filter(product=self)
    
    def gallery(self):
        return Gallery.objects.filter(product=self)
    
    def variants(self):
        return Variant.objects.filter(product=self)
    
    def vendor_orders(self):
        return OrderItem.objects.filter(product=self, vendor=self.vendor)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name) + "-" + str(shortuuid.uuid().lower()[:2])
        super(Product, self).save(*args, **kwargs)
        
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Nombre de la variante")
    
    def items(self):
        return VariantItem.objects.filter(variant=self)
    
    def __str__(self):
        return self.name
    
class VariantItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="variant_items")
    title = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Título")
    content = models.TextField(max_length=1000, null=True, blank=True, verbose_name="Contenido")
    
    def __str__(self):
        return self.variant.name
    
class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to="images")
    gallery_id = ShortUUIDField(length=6, max_length=10, prefix="GAL", alphabet="1234567890")
    
    def __str__(self):
        return f"{self.product.name} - image"
    
    class Meta:
        verbose_name_plural = "Galería"
    
class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=0, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    cart_id = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.cart_id} - {self.product.name}'
    
class Coupon(models.Model):
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=100)
    discount = models.IntegerField(default=1)
    
    def __str__(self):
        return self.code
    
class Order(models.Model):
    vendors = models.ManyToManyField(user_models.User, blank=True)
    customer = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True, related_name="customer")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    service_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=100, default="Processing")
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=100, default=None, null=True, blank=True)
    order_status = models.CharField(choices=ORDER_STATUS, max_length=100, default="Pending")
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="El total original antes de cualquier descuento.")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="El total ahorrado por el cliente.")
    address = models.ForeignKey("customer.Address", on_delete=models.SET_NULL, null=True, blank=True)
    coupons = models.ManyToManyField(Coupon, blank=True)
    order_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    payment_id = models.CharField(max_length=1000, null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name_plural = "Pedidos"
        ordering = ["-date"]
    
    def __str__(self):
        return self.order_id
    
    def order_items(self):
        return OrderItem.objects.filter(order=self)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_status = models.CharField(choices=ORDER_STATUS, max_length=100, default="Pending")
    shipping_service = models.CharField(choices=SHIPPING_SERVICE, default=None, max_length=100, null=True, blank=True)
    tracking_id = models.CharField(max_length=1000, default=None, null=True, blank=True)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    initial_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total general antes de todo el monto.")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="El total ahorrado por el cliente.")
    coupon = models.ManyToManyField(Coupon, blank=True)
    applied_coupon = models.BooleanField(default=False)
    item_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890")
    vendor = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, related_name="vendor_order_items")
    date = models.DateTimeField(default=timezone.now)
    
    def order_id(self):
        return f"{self.order.order_id}"
    
    def __str__(self):
        return self.item_id
    
    class Meta:
        ordering = ["-date"]
        
class Review(models.Model):
    user = models.ForeignKey(user_models.User, on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    review = models.TextField(null=True, blank=True)
    repply = models.TextField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING, default=None)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} calificó a {self.product.name}"
    

