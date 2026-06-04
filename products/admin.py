from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review, Profile

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    
    list_display = ['id', 'user', 'first_name', 'last_name', 'email', 'city', 'is_paid', 'status', 'created']
    
    list_filter = ['is_paid', 'status', 'created']
     
    list_editable = ['is_paid', 'status']
    inlines = [OrderItemInline]

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Profile)