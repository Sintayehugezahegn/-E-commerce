from django.contrib import admin
from .models import Category, Product, Order, OrderItem

# በትዕዛዙ ውስጥ ያሉ እቃዎችን በዝርዝር ለማሳየት
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # ተጨማሪ ባዶ መስመር እንዳያሳይ
    readonly_fields = ['product', 'price', 'quantity'] # አድሚኑ እንዳይቀይረው

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # አድሚን ገፁ ላይ በዝርዝር የሚታዩት ነገሮች
    list_display = ['id', 'first_name', 'last_name', 'email', 'status', 'is_paid', 'created']
    
    # በጎን በኩል ማጣሪያ (Filter) እንዲኖር
    list_filter = ['is_paid', 'status', 'created']
    
    # አድሚኑ ገጹን ሳይከፍት እቃው መላኩን እዚሁ እንዲቀይር
    list_editable = ['status', 'is_paid']
    
    # በትዕዛዙ ውስጥ ያሉትን እቃዎች (OrderItem) በዝርዝር ከታች እንዲያሳይ
    inlines = [OrderItemInline]
    
    # የአድሚኑን ገጽ አቀማመጥ ማስተካከል (መልእክቱን ለማድመቅ)
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'first_name', 'last_name', 'email', 'address', 'city')
        }),
        ('Order Status', {
            'fields': ('status', 'is_paid', 'payment_reference')
        }),
        ('Message from Customer', {
            'fields': ('customer_note',),
            'description': 'ይህ ገዢው በቼክአውት ወቅት የጻፈልህ ልዩ መልእክት ነው።'
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available', 'created']
    list_filter = ['category', 'available']
    list_editable = ['price', 'available']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']