from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages  # ለኤረር መልዕክት ማሳያ
from .models import Product, Category, Order, OrderItem, Review, Profile
from .cart import Cart

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # ማረጋገጫ፦ አዲስ የሚመዘገብ ዩዘር በጭራሽ አድሚን ወይም ሻጭ (Staff) እንዳይሆን በግድ False እናደርገዋለን
            user.is_staff = False
            user.is_superuser = False
            user.save()
            
            login(request, user)
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    return render(request, 'products/product_list.html', {'products': products, 'categories': categories})

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    return render(request, 'products/product_detail.html', {'product': product, 'reviews': reviews})

@login_required
def add_review(request, id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=id)
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return redirect('product_detail', id=product.id)
    return redirect('product_list')

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            profile.image = request.FILES['image']
            profile.save()
            return redirect('profile')

    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'products/profile.html', {'orders': orders, 'profile': profile})

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
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
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.user.email,
            address=request.POST.get('address'),
            city=request.POST.get('city')
        )
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
        cart.clear()
        return render(request, 'products/payment_success.html', {'order': order})
    return render(request, 'products/checkout.html', {'cart': cart})