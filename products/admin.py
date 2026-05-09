from django.contrib import admin
from .models import Category, Product, Order, OrderItem, Review
from django.utils.html import format_html

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # 'status' ን እዚህ ዝርዝር ውስጥ መጨምር አለብን editable እንዲሆን
    list_display = [
        'id', 'customer_name', 'status', 'status_colored', 'is_paid', 
        'payment_reference', 'total_price_display', 'created'
    ]
    list_filter = ['status', 'is_paid', 'created']
    search_fields = ['first_name', 'last_name', 'email', 'payment_reference']
    
    # 'status' አሁን እዚህ መጠቀም ይቻላል ምክንያቱም list_display ውስጥ ስላለ
    list_editable = ['status', 'is_paid'] 
    inlines = [OrderItemInline]
    
    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer_name.short_description = 'Customer'
    
    def total_price_display(self, obj):
        return f"${obj.total_cost}"
    total_price_display.short_description = "Total Amount"

    # ሁኔታውን በቀለም ለማየት (ለማሳመር ብቻ)
    def status_colored(self, obj):
        colors = {
            'Pending': '#FFA500',   # Orange
            'Processing': '#007BFF', # Blue
            'Shipped': '#6f42c1',    # Purple
            'Delivered': '#28a745',  # Green
            'Cancelled': '#dc3545',  # Red
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<strong style="color: {};">● {}</strong>',
            color,
            obj.status
        )
    status_colored.short_description = "Live Status"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['image_tag', 'name', 'category', 'price', 'available']
    list_filter = ['category', 'available']
    list_editable = ['price', 'available']
    
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height:45px; border-radius:5px; border: 1px solid #ddd;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Preview'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating_stars', 'created_at']
    readonly_fields = ['created_at']

    def rating_stars(self, obj):
        return "⭐" * obj.rating
    rating_stars.short_description = 'Rating'

admin.site.register(Category)

# የአስተዳዳሪ ገጹ ርዕሶች
admin.site.site_header = "Ethio Shop Admin Panel"
admin.site.site_title = "Ethio Shop Portal"
admin.site.index_title = "Store Management"