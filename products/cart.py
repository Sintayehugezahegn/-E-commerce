from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        p_id = str(product.id)
        if p_id not in self.cart:
            self.cart[p_id] = {'quantity': 0, 'price': str(product.price)}
        self.cart[p_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        p_id = str(product.id)
        if p_id in self.cart:
            del self.cart[p_id]
            self.save()

    def __iter__(self):
        p_ids = self.cart.keys()
        products = Product.objects.filter(id__in=p_ids)
        cart = self.cart.copy()
        for p in products:
            cart[str(p.id)]['product'] = p
        for item in cart.values():
            if 'product' in item:
                item['price'] = Decimal(item['price'])
                item['total_price'] = item['price'] * item['quantity']
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(i['price']) * i['quantity'] for i in self.cart.values() if 'price' in i)

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()