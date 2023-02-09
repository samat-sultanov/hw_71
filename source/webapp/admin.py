from django.contrib import admin

from webapp.models import Product, Order, Cart, OrderProduct


class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'amount', 'price')
    list_display_links = ('pk', 'name')
    list_filter = ('category',)
    search_fields = ('name',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'phone', 'created_at']
    list_display_links = ['name']
    exclude = []
    search_fields = ['name', 'address']
    ordering = ('-created_at',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart)
admin.site.register(OrderProduct)
