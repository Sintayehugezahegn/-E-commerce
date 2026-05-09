import requests
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Order, OrderItem, Review

# የካርት ፋይሉን ለማግኘት
try:
    from cart.cart import Cart
except ImportError:
    from .cart import Cart 

# 1. የምርቶች ዝርዝር ማሳያ (Home Page)
def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    query = request.GET.get('q')
    selected_category = request.GET.get('category')

    if query:
        products = products.filter(name__icontains=query)
    if selected_category:
        products = products.filter(category_id=selected_category)

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query
    })

# 2. የአንድ ምርት ዝርዝር መረጃ
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    reviews = product.reviews.all().order_by('-created_at')
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews
    })

# 3. የገበያ ጋሪ ዝርዝር (Cart Page)
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'products/cart_detail.html', {'cart': cart})

# 4. ወደ ጋሪ መጨመሪያ
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    return redirect('cart_detail')

# 5. ከጋሪ መቀነሻ
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

# 6. የክፍያ ገጽ (Checkout)
@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('product_list')
    
    # 1 ዶላር = 150 ብር ስሌት
    dollar_total = cart.get_total_price()
    exchange_rate = 150
    etb_total = float(dollar_total) * exchange_rate

    if request.method == 'POST':
        tx_ref = str(uuid.uuid4())
        
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            customer_note=request.POST.get('note'),
            payment_reference=tx_ref
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )

        # Chapa ክፍያ
        chapa_url = "https://api.chapa.co/v1/transaction/initialize"
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        payload = {
            "amount": str(etb_total),
            "currency": "ETB",
            "email": order.email,
            "tx_ref": tx_ref,
            "callback_url": f"http://{request.get_host()}/payment-success/{order.id}/",
            "return_url": f"http://{request.get_host()}/payment-success/{order.id}/",
        }
        
        try:
            response = requests.post(chapa_url, json=payload, headers=headers)
            res = response.json()
            if res.get('status') == 'success':
                cart.clear()
                return redirect(res['data']['checkout_url'])
            else:
                messages.error(request, f"Chapa Error: {res.get('message')}")
        except Exception as e:
            messages.error(request, "Connection error to payment gateway.")

    return render(request, 'products/checkout.html', {
        'cart': cart,
        'etb_total': etb_total
    })

# 7. ክፍያ ሲሳካ
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_paid = True
    order.save()
    return render(request, 'products/payment_success.html', {'order': order})

# 8. አስተያየት መጨመሪያ
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
    return redirect('product_detail', id=product_id)