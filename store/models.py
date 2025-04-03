from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from userauths import models as user_models
from ckeditor.fields import RichTextField
from django.utils.timezone import now
from django.utils.text import slugify
from django.contrib.auth.models import User
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

SLIDER_STATUS = (
    ("Active", "Activo"),
    ("Inactive", "Inactivo"),
)

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class AboutUs(models.Model):
    title = models.CharField(max_length=255, verbose_name="Título")
    content = CKEditor5Field("Contenido", config_name="extends")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Sobre Nosotros"
        verbose_name_plural = "Sobre Nosotros"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title
    
class MensajeContacto(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    asunto = models.CharField(max_length=255, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"

    def __str__(self):
        return f"{self.nombre} - {self.asunto}"

class StoreSettings(models.Model):
    store_name = models.CharField(max_length=255, verbose_name="Nombre de la Tienda")
    logo = models.ImageField(upload_to="settings/", verbose_name="Logo de la Tienda")
    favicon = models.ImageField(upload_to="settings/", verbose_name="Favicon (Ícono de pestaña)")
    
    address = models.TextField(verbose_name="Dirección")
    phone = models.CharField(max_length=20, verbose_name="Teléfono")
    email = models.EmailField(verbose_name="Correo Electrónico")

    facebook = models.URLField(blank=True, null=True, verbose_name="Facebook")
    instagram = models.URLField(blank=True, null=True, verbose_name="Instagram")
    twitter = models.URLField(blank=True, null=True, verbose_name="Twitter")
    youtube = models.URLField(blank=True, null=True, verbose_name="YouTube")
    linkedin = models.URLField(blank=True, null=True, verbose_name="LinkedIn")

    seo_title = models.CharField(max_length=255, verbose_name="Título SEO")
    seo_description = models.TextField(verbose_name="Descripción SEO")
    seo_keywords = models.CharField(max_length=500, verbose_name="Palabras Clave SEO")

    STTRIPE_PUBLIC_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="Stripe Public Key")
    STTRIPE_SECRET_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="Stripe Secret Key")

    PAYPPAL_CLIENT_ID = models.CharField(max_length=255, blank=True, null=True, verbose_name="PayPal Client ID")
    PAYPPAL_SECRET_ID = models.CharField(max_length=255, blank=True, null=True, verbose_name="PayPal Secret ID")

    FLUTTERWAVEE_PUBLIC_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="Flutterwave Public Key")
    FLUTTERWAVEE_PRIVATE_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="Flutterwave Private Key")

    PAYSTTACK_PUBLIC_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="Paystack Public Key")
    PAYSTTACK_PRIVATE_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="Paystack Private Key")

    MAILGUN_API_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mailgun API Key")
    MAILGUN_SENDER_DOMAIN = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mailgun Sender Domain")

    FROM_EMAIL = models.EmailField(blank=True, null=True, verbose_name="Correo de Envío")
    EMAIL_BACKEND = models.CharField(max_length=255, blank=True, null=True, verbose_name="Backend de Correo")
    DEFAULT_FROM_EMAIL = models.EmailField(blank=True, null=True, verbose_name="Correo Predeterminado")
    SERVER_EMAIL = models.EmailField(blank=True, null=True, verbose_name="Correo del Servidor")

    DJANGO_RECAPTCHA_PUBLIC_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="reCAPTCHA Public Key")
    DJANGO_RECAPTCHA_PRIVATE_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="reCAPTCHA Private Key")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Configuración"
        verbose_name_plural = "Configuraciones"

    def __str__(self):
        return self.store_name

class Slider(models.Model):
    slider_id = ShortUUIDField(length=6, max_length=25, alphabet="1234567890", unique=True, verbose_name="ID del Slider")
    title = models.CharField(max_length=255, verbose_name="Título")
    subtitle = models.CharField(max_length=255, blank=True, null=True, verbose_name="Subtítulo")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    image = models.ImageField(upload_to="sliders/", verbose_name="Imagen del Slider")
    
    has_button = models.BooleanField(default=False, verbose_name="¿Tiene botón?")
    button_text = models.CharField(max_length=50, blank=True, null=True, verbose_name="Texto del Botón")
    button_link = models.URLField(max_length=500, blank=True, null=True, verbose_name="Enlace del Botón")

    status = models.CharField(choices=SLIDER_STATUS, max_length=10, default="Active", verbose_name="Estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generar un slider_id si no existe
        if not self.slider_id:
            self.slider_id = slugify(self.title)[:6] + str(timezone.now().timestamp())[-4:]

        # Si `has_button` es False, limpiar los valores de button_text y button_link
        if not self.has_button:
            self.button_text = None
            self.button_link = None

        super(Slider, self).save(*args, **kwargs)

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
    
POST_STATUS = (
    ("Published", "Publicado"),
    ("Draft", "Borrador"),
    ("Archived", "Archivado"),
)

class CategoryPost(models.Model):
    title = models.CharField(max_length=255, verbose_name="Categoría")
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías de posts"
    
    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=255, verbose_name="Etiquetas")
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = "Etiqueta"
        verbose_name_plural = "Etiquetas"
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    image = models.ImageField(upload_to="blog_images/", verbose_name="Imagen Destacada", null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name="Título")
    short_content = models.TextField(verbose_name="Contenido corto", default="Sin resumen", null=True, blank=True)
    content = CKEditor5Field("Contenido", config_name="extends")
    category = models.ForeignKey(CategoryPost, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name="blog_posts", blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    status = models.CharField(choices=POST_STATUS, max_length=10, default="Draft")
    author = models.ForeignKey('userauths.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    class Meta:
        verbose_name = "Post del Blog"
        verbose_name_plural = "Posts del Blog"
        ordering = ["-created_at"]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(shortuuid.uuid().lower()[:6])
        super(BlogPost, self).save(*args, **kwargs)


class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    author = models.CharField(max_length=255, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Correo Electrónico")
    comment = models.TextField(verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
    
    def __str__(self):
        return f"Comentario de {self.author} en {self.post.title}"

