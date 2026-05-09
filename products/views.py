from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Order, OrderItem, Review
from .cart import Cart

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'products/product_list.html', {
        'products': products, 
        'categories': categories
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    reviews = product.reviews.all().order_by('-created_at')
    return render(request, 'products/product_detail.html', {'product': product, 'reviews': reviews})

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'products/cart_detail.html', {'cart': cart})

@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('product_list')
    
    if request.method == 'POST':
        bank = request.POST.get('bank_name')
        ref = request.POST.get('payment_reference')
        
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.user.email,
            address=request.POST.get('address'),
            payment_reference=f"{bank}: {ref}"
        )
        
        for item in cart:
            OrderItem.objects.create(
                order=order, product=item['product'], 
                price=item['price'], quantity=item['quantity']
            )
        
        cart.clear()
        return redirect('payment_success', order_id=order.id)
            
    return render(request, 'products/checkout.html', {'cart': cart})

def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'products/payment_success.html', {'order': order})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'products/profile.html', {'orders': orders})

@login_required
def add_review(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )
        messages.success(request, "Review added!")
    return redirect('product_detail', id=product_id)