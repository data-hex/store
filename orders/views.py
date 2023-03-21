from django.views.generic.edit import CreateView

# Create your views here.
class OrderCreateView(CreateView):
    template_name = 'orders/order-create.html'