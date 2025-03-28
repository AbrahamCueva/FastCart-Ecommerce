from django.urls import path
from vendor import views

app_name = "vendor"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("products/", views.products, name="products"),
    
    path("orders/", views.orders, name="orders"),
    path("order_detail/<order_id>/", views.order_detail, name="order_detail"),
    path("order_item_detail/<order_id>/<item_id>", views.order_item_detail, name="order_item_detail"),
    path("update_order_status/<order_id>/", views.update_order_status, name="update_order_status"),
    path("update_order_item_status/<order_id>/<item_id>/", views.update_order_item_status, name="update_order_item_status"),
    
    path("coupons/", views.coupons, name="coupons"),
    path("coupon_create/", views.coupon_create, name="coupon_create"),
    path("update_coupon/<id>", views.update_coupon, name="update_coupon"),
    path("delete_coupon/<id>", views.delete_coupon, name="delete_coupon"),
    
    
    path("reviews/", views.reviews, name="reviews"),
    path("update_repply/<id>", views.update_repply, name="update_repply"),
]