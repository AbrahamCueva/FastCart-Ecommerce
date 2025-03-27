from django.urls import path
from customer import views

app_name = "customer"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("orders/", views.orders, name="orders"),
    path("order_detail/<order_id>/", views.order_detail, name="order_detail"),
    path("order_item_detail/<order_id>/<item_id>/", views.order_item_detail, name="order_item_detail"),
    path("whislist/", views.wishlist, name="wishlist"),
    path("add_to_wishlist/<id>/", views.add_to_whislist, name="add_to_whislist"),
    path("remove_from_wishlist/<id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
    path("notis/", views.notis, name="notis"),
    path("mark_noti_seen/<id>/", views.mark_noti_seen, name="mark_noti_seen"),
    path("addresses/", views.addresses, name="addresses"),
    path("address_detail/<id>/", views.address_detail, name="address_detail"),
    path("address_create/", views.address_create, name="address_create"),
    path("delete_addresses/<id>/", views.delete_addresses, name="delete_addresses"),
    path("profile/", views.profile, name="profile"),
    path("change_password/", views.change_password, name="change_password"),
]