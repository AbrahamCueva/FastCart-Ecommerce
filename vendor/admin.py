from django.contrib import admin
from vendor import models as vendor_models

class VendorAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'user', 'country', 'vendor_id', 'date']
    search_fields = ['store_name', 'user__username', 'vendor_id']
    prepopulated_fields = {'slug': ('store_name',)}
    list_filter = ['date', 'country']

class PayoutAdmin(admin.ModelAdmin):
    list_display = ['payout_id', 'vendor', 'item', 'amount', 'date']
    search_fields = ['payout_id', 'vendor__store_name', 'item__product__order_id']
    list_filter = ['date', 'vendor']
    
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'account_type', 'bank_name', 'account_number', 'account_name']
    search_fields = ['vendor__store_name', 'bank_name', 'account_number']
    list_filter = ['account_type']
    
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ['user','type', 'order', 'seen']
    list_editable = ['order']
    
admin.site.register(vendor_models.Vendor, VendorAdmin)
admin.site.register(vendor_models.Payout, PayoutAdmin)
admin.site.register(vendor_models.BankAccount, BankAccountAdmin)
admin.site.register(vendor_models.Notifications, NotificationsAdmin)

