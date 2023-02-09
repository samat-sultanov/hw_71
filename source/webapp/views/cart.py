from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView
from django.contrib.sessions.models import Session

from webapp.forms import CartForm, OrderForm
from webapp.models import Cart, Product, Order, OrderProduct


class CartAddView(CreateView):
    model = Cart
    form_class = CartForm

    def form_valid(self, form):
        if not self.request.session.session_key:
            self.request.session.save()
        product = get_object_or_404(Product, pk=self.kwargs.get("pk"))
        qty = form.cleaned_data.get("qty")

        if Cart.objects.filter(product_id=product.pk):
            cart_product_qty = 0
            cart_product = Cart.objects.filter(product_id=product.pk)
            for i in cart_product:
                cart_product_qty += i.qty
        else:
            cart_product_qty = 0

        if qty > product.amount or (qty + cart_product_qty) > product.amount:
            messages.error(self.request, f"Количество товара {product.name} с вычетом товара в корзинах пользователя: {product.amount-cart_product_qty}. Добавить {qty} штук в корзину не получилось")
        else:
            cart_product, is_created = Cart.objects.get_or_create(product=product, user_session=Session.objects.get(
                session_key=self.request.session.session_key))
            if is_created:
                cart_product.qty = qty
            else:
                cart_product.qty += qty
            cart_product.user_session = Session.objects.get(session_key=self.request.session.session_key)
            cart_product.save()
            messages.success(self.request, f'{product.name}: {qty} штук добавлено в корзину')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        next = self.request.GET.get("next")
        if next:
            return next
        return reverse("webapp:index")


class CartView(ListView):
    model = Cart
    template_name = "cart/cart_view.html"
    context_object_name = "cart"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        cart = self.get_queryset()
        context['form'] = OrderForm()
        context['total'] = 0
        for product in cart:
            context['total'] += product.get_product_total()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_session=self.request.session.session_key)


class CartDeleteView(DeleteView):
    model = Cart
    success_url = reverse_lazy('webapp:cart')

    def get(self, request, *args, **kwargs):
        messages.warning(self.request, f"{self.get_object()} штук удалено из корзины")
        return self.delete(request, *args, **kwargs)


class CartDeleteOneView(DeleteView):
    model = Cart
    success_url = reverse_lazy('webapp:cart')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        cart = self.object
        cart.qty -= 1
        if cart.qty < 1:
            messages.warning(self.request, f"{self.get_object()} штук удалено из корзины")
            cart.delete()
        else:
            cart.save()
            messages.warning(self.request, f"{self.get_object()} штук удалено из корзины")
        return HttpResponseRedirect(success_url)


class OrderCreate(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('webapp:index')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.name = self.request.user.username
        order = form.save()

        products = []
        order_products = []

        if self.request.user.is_authenticated:
            for item in Cart.objects.filter(user_session_id=self.request.session.session_key):
                order_products.append(OrderProduct(product=item.product, qty=item.qty, order=order))
                item.product.amount -= item.qty
                products.append(item.product)
        else:
            for item in Cart.objects.filter(user_session_id=self.request.session.session_key):
                order_products.append(OrderProduct(product=item.product, qty=item.qty, order=order))
                item.product.amount -= item.qty
                products.append(item.product)

        OrderProduct.objects.bulk_create(order_products)
        Product.objects.bulk_update(products, ("amount",))
        Cart.objects.filter(user_session_id=self.request.session.session_key).delete()
        return HttpResponseRedirect(self.success_url)
