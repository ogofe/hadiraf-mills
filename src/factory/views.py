import csv
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import StreamingHttpResponse, FileResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, time, date
from django.contrib import messages
from utils import (
    Echo, get_dataset, errors
)
from .models import (
    Product, Production, Ingredient, Customer,
    Shipment, Staff_Permission, MEASURING_UNITS,
    Resource, Order_Item, Worker, Invoice,
)




def get_time(time_str):
    t = time_str.split(' ')
    period = t[1].lower()
    hour = int(t[0].split(':')[0])
    _min = int(t[0].split(':')[1])
    if period == 'am':
        recv_time = time(hour, _min)
    else:
        # recv_time = None
        if hour < 12:
            recv_time = time(hour+12, _min)
        elif hour == 12:
            recv_time = time(0, _min)
    return recv_time

def django_date(date_str):
    month, day, year = tuple(date_str.split('/'))
    recv_date = date(int(year), int(month), int(day))
    return recv_date



class Overview_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/pages/overview.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Overview"
        return context

# Resources    
    
class Resources_Page(LoginRequiredMixin, ListView):
    login_url = 'work:login'
    template_name = 'work/pages/inventory.html'
    queryset = Resource.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["inventory"] = self.queryset
        context["title"] = "Resources"
        return context

    
class Create_Resource_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/forms/create-resource.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Resource"
        return context

    def post(self, request, **kwargs):
        data = request.POST
        new = Resource(
            name=data['name'],
            quantity=data['stock'],
            unit=data['unit'],
            weight_in_kg=data['weight']
            )
        new.save()
        messages.success(request, "Successfully added new resource %s" % new.name)
        return redirect('work:resources')


    

# Shipments    
    
class Shipments_Page(LoginRequiredMixin, ListView):
    login_url = 'work:login'
    template_name = 'work/pages/shipments.html'
    
    def get_queryset(self, **kwargs):
        qs = Shipment.objects.all().order_by('-id')
        self.queryset = qs
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shipments"] = self.queryset
        context["title"] = "Shipments"
        return context

    
class Create_Shipment_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/forms/create-shipment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Invoice"
        context["stock"] = Resource.objects.all()
        return context

    def post(self, request, **kwargs):
        data = request.POST
        items = data.getlist('resource')
        recv_time = get_time(data['time'])
        recv_date = django_date(data['date'])
        rec  = Shipment(
            received_from = data['from'] if 'from' in data else None,
            date_received = recv_date,
            time_received = recv_time,
            )
        rec.save()
        for item in items:
            new = Resource.objects.get_or_create(name=item.split(':-:')[0])[0]
            new.quantity += int(item.split(':-:')[1])                
            new.save()
            rec.add_item(new)
        messages.success(request, "Successfully added new shipment %s" % rec.shipment_id)
        return redirect('work:shipments')


class Shipment_Detail_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/pages/shipment-detail.html'
    queryset = Shipment.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["shipment"] = self.queryset.get(shipment_id=self.kwargs['shipment'])
        context["title"] = "Shipment Detail"
        return context
    


# Invoices    
    
class Invoices_Page(LoginRequiredMixin, ListView):
    login_url = 'work:login'
    template_name = 'work/pages/invoices.html'
    queryset = Invoice.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoices"] = self.queryset
        context["title"] = "Invoices"
        return context

    
class Create_Invoice_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/forms/create-invoice.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Invoice"
        context["inventory"] = Product.objects.all()
        return context

    def post(self, request, **kwargs):
        data = request.POST
        items = data.getlist('resource')
        try:
            customer = Customer.objects.get(phone_number=data['customer-phone'])
        except Customer.DoesNotExist:
            customer = Customer(
                name = data['customer-name'],
                phone_number = data['customer-phone'],
                email = data['customer-email'] if data['customer-email'] else None,
                delivery_address = data['delivery-address'],
                )
            customer.save()

        invoice = Invoice(
            customer=customer,
            to_be_delivered=True if data['delivery'] == 'yes' else False,
            date_of_payment=django_date(data['date-paid']) if 'date-paid' in data else None,
            )
        invoice.save()

        for item in items:
            order = Order_Item(
                quantity=int(item.split(':-:')[1]),
                product = Product.objects.get(name=item.split(':-:')[0]),
                invoice=invoice
                )
            order.save()
            invoice.add_item(order)

        messages.success(request, "Successfully added new invoice %s" % invoice.number)
        if 'pay-ahead' in data and data['pay-ahead']:
            return redirect('core:pay-invoice', invoice=invoice.number)
        return redirect('work:invoices')


class Invoice_Detail_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/pages/invoice-detail.html'
    queryset = Invoice.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["invoice"] = self.queryset.get(number=self.kwargs['invoice'])
        context["title"] = "Invoice Detail"
        return context
    

# Staff
    
class Staff_Page(LoginRequiredMixin, ListView):
    login_url = 'work:login'
    template_name = 'work/pages/staffs.html'
    
    def get_queryset(self):
        qs = Worker.objects.all().order_by('-id')
        self.queryset = qs
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["accounts"] = self.queryset
        context["title"] = "Staffs"
        return context
    
    
class Create_Staff_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/forms/create-staff.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add A Staff"
        return context

    def post(self, request, **kwargs):
        data = request.POST
        perms = data.getlist('perms')
        staff = Worker(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone'],
            email=data['email'],
            password='12345678',
            gender=data['gender'],
            role = data['role'],
            )
        staff.create()
        for perm in perms:
            staff.add_perm(Permission.objects.get(code_name=perm))
        messages.success(request, "Successfully created new staff account for %s" % staff.name)
        return redirect('work:staff')


# Customers    
    
class Customers_Page(LoginRequiredMixin, ListView):
    login_url = 'work:login'
    template_name = 'work/pages/customers.html'
    queryset = Customer.objects.all()
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customers"] = self.queryset
        context["title"] = "Customers"
        return context
    
    
class Add_Customer_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/forms/create-customer.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Customer"
        return context
    
    def post(self, request, **kwargs):
        data = request.POST
        new = Customer(
                name = data['name'],
                phone_number=data['phone'],
                email=data['email'] if 'email' in data else None,
                delivery_address = data['address'] if 'address' in data else None
            )
        new.save()
        messages.success(request, "Successfully added new customer %s" % new.name)
        return redirect('work:customers')



# Products

class Products_Page(LoginRequiredMixin, ListView):
    login_url = 'work:login'
    template_name = 'work/pages/products.html'

    def get_queryset(self, **kwargs):
        qs = Product.objects.all().order_by('-id')
        self.queryset = qs
        return qs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = self.queryset
        context["title"] = "Products"
        return context


class Create_Product_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/forms/create-product.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add Product"
        context["measurements"] = MEASURING_UNITS
        return context    
    
    def post(self, request, **kwargs):
        data = request.POST
        img = request.FILES['image']
        new_prod = Product(
            name=data['name'],
            weight_in_kg=data['weight'],
            price=data['price'],
            available_stock=data['stock'],
            measurement=data['unit'],
            image=img or None,
            about=data['about'] or None,
            online_sale = True if data['online'] == 'yes' else False
            )
        new_prod.save()
        messages.success(request, "Successfully added new product.")
        return redirect('work:products')


# Production
    
class Production_Page(LoginRequiredMixin, ListView):
    login_url = 'work:login'
    template_name = 'work/pages/production.html'
    queryset = Production.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Production Records"
        context["cycles"] = self.queryset
        return context


class Create_Production_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/forms/create-production.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        context["resources"] = Resource.objects.all()
        context["title"] = "Records"
        return context

    def post(self, request, **kwargs):
        data = request.POST
        cycle = Production(
            product=Product.objects.get(name=data['product']),
            date_of_production = django_date(data['date']) or datetime.now().date(),
            time_of_production = get_time(data['time']) or datetime.now().time()
            )
        cycle.save()
        res = data.getlist('resource')
        for item in res:
            item = item.split(':-:')
            use = Ingredient(
                production=cycle,
                resource= Resource.objects.get(name=item[0]),
                quantity= int(item[1])
            )
            use.resource.quantity -= use.quantity
            use.resource.save()
            use.save()
            cycle.add_usage(use)
            messages.success(request, "Successfully started new production %s" % cycle.production_id)
        return redirect('work:production')

    
class Production_Detail_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/pages/production-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cycle"] = Production.objects.get(production_id=self.kwargs['production_id'])
        context["title"] = "Production Detail"
        return context


def set_production_output(request, cycle):
    production = Production.objects.get(production_id=cycle)
    data = request.POST
    production.output = int(data['qty'])
    production.save()
    messages.info(request, "Successfully added output volume to %s" % cycle)
    return redirect(request.META['HTTP_REFERER'])




class Metrics_Page(LoginRequiredMixin, TemplateView):
    login_url = 'work:login'
    template_name = 'work/pages/metrics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Metrics"
        return context
    
    
class Login_Page(TemplateView):
    template_name = 'work/login.html'
    
    def post(self, request):
        data = request.POST
        user = authenticate(request, username=data['username'], password=data['password'])
        if user:
            login(request, user)
            return redirect('work:overview')
        messages.error(request, "Incorrect username or password")
        return redirect(request.META['HTTP_REFERER'])
    

def sign_out(request):
    logout(request)
    return redirect('core:home')


def generate_report(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows from the dataset.
    # first check what data is required
    data = request.POST
    dataset = get_dataset(data['report_on'])
    rows = dataset
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in rows),
    content_type="text/csv")
    response['Content-Disposition'] = 'attachment; \
        filename="hadiraf-%s-report-%s.csv"' % (data['query'],
                                                    f"for-{data['date']}" if 'date' in data else str(datetime.now().date()))
    return response