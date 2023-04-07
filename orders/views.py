import uuid
from http import HTTPStatus

from yookassa import Configuration, Payment

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.conf import settings

from common.views import TitleMixin
from orders.forms import OrderForm
from orders.models import Order
from products.models import Basket

Configuration.account_id = settings.YOUKASSA_ACCOUNT_ID
Configuration.secret_key = settings.YOUKASSA_SECRET_KEY


class SuccessTemplateView(TitleMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'Store - Спасибо за заказ!'


class CanceledTemplateView(TemplateView):
    template_name = 'orders/cancled.html'

# Create your views here.

class OrderListView(TitleMixin, ListView):
    template_name = 'orders/orders.html'
    title = 'Store - Заказы'
    queryset = Order.objects.all()
    ordering = ('-created')

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(initiator=self.request.user)


class OrderDetailView(DetailView):
    template_name = 'orders/order.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['title'] = f'Store - Заказ # {self.object.id}'
        return context

flag = False
class OrderCreateView(TitleMixin, CreateView):
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:order_create')
    title = 'Store - Оформление заказа'


    def post(self, request, *args, **kwargs):
        super(OrderCreateView, self).post(request, *args, **kwargs)
        baskets = Basket.objects.filter(user=self.request.user)
        global flag

        payment = Payment.create({
            "amount": {
                "value": float(baskets.total_sum()),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": '{}{}'.format(settings.DOMAIN_NAME, reverse('orders:order_success'))
            },
            "capture": True,
            "description": f" Заказ № {self.object.id}",

        }, uuid.uuid4())
        # костыль, так как у юкассы нет на тестовом заказе ответов вебхука без подключения домена и ssl
        flag = True
        if flag:
            order = Order.objects.get(id=self.object.id)
            order.update_after_payment()
        return HttpResponseRedirect(payment.confirmation.confirmation_url, status=HTTPStatus.SEE_OTHER)

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        return super(OrderCreateView, self).form_valid(form)

