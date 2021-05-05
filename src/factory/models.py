from django.db import models
from time import time
from django.contrib.auth.models import User
from utils import (
    fetch_settings,
    alter_setting,
)
from random import randint
from django.conf import settings


def stamp():
    return str(time()).split('.')[1]

def create_invoice_number():
    char = str(time()).split('.')
    return f'{char[0][:3]}{char[1][:3]}'

def create_staff_id():
    return f'{randint(1111, 9999)}-{randint(2000, 7000)}'


MEASURING_UNITS = (
    ('bag', 'Bag'),
    ('box', 'Box / Carton'),
    ('crate', 'Crate'),
)

class Customer(models.Model):
    name                = models.CharField(max_length=200)
    phone_number        = models.CharField(max_length=20, unique=True)
    email               = models.EmailField(blank=True, null=True)
    delivery_address    = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.name


class Staff_Permission(models.Model):
    code_name           = models.CharField(max_length=200)
    verbose_name        = models.CharField(max_length=200)

    def __str__(self):
        return self.code_name


GENDER = (
    ('M', 'Male'),
    ('F', 'Female'),
    )
class Worker(models.Model):
    staff_id            = models.CharField(max_length=30, default=create_staff_id)
    first_name          = models.CharField(max_length=50)
    last_name           = models.CharField(max_length=50)
    email               = models.EmailField()
    phone_number        = models.CharField(max_length=20)
    password            = models.CharField(max_length=150)
    date_of_employment  = models.DateField(blank=True, null=True)
    role                = models.CharField(max_length=70, blank=True, null=True)
    gender              = models.CharField(max_length=1, choices=GENDER)
    permissions         = models.ManyToManyField(Staff_Permission, blank=True)
    
    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def remove_perm(self, perm):
        self.permissions.remove(perm)
        self.save()

    def add_perm(self, perm):
        self.permissions.add(perm)
        self.save()

    def is_female(self):
        if self.gender == "F":
            return True
        return False

    def is_male(self):
        if self.gender == "M":
            return True
        return False
        
    def __str__(self):
        return self.name   
    
    def create(self):
        user = User(
            first_name  = self.first_name,
            last_name   = self.last_name,
            username    = self.staff_id,
            email       = self.email
        )
        user.set_password('12345678')
        user.save()
        self.password = user.password
        self.save()
    

class Product(models.Model):
    name                = models.CharField(max_length=150)
    price               = models.FloatField()
    about               = models.TextField(blank=True, null=True)
    available_stock     = models.IntegerField()
    measurement         = models.CharField(max_length=30, choices=MEASURING_UNITS, default='bag')
    weight_in_kg        = models.FloatField()
    online_sale         = models.BooleanField(default=True)
    image               = models.ImageField(upload_to='product-images/', blank=True, null=True)

    def __str__(self):
        return self.name
    

class Resource(models.Model):
    name                = models.CharField(max_length=100)
    quantity            = models.IntegerField(default=0)
    shipment            = models.ForeignKey("Shipment", blank=True, null=True, on_delete=models.SET_NULL)
    unit                = models.CharField(max_length=30, choices=MEASURING_UNITS, default='bag')
    entry               = models.DateTimeField(auto_now=True)
    weight_in_kg        = models.IntegerField()

    def __str__(self):
        return self.name

    def date(self):
        return self.entry.date()

    def time(self):
        return self.entry.time()


class Shipment(models.Model):
    items               = models.ManyToManyField("Resource", blank=True, related_name='received')
    date_received       = models.DateField()
    time_received       = models.TimeField()
    received_from       = models.CharField(max_length=100, blank=True, null=True)
    shipment_id         = models.CharField(max_length=12, default=stamp)

    def __str__(self):
        return self.shipment_id

    def add_item(self, item):
        self.items.add(item)
        self.save()

    def items_to_string(self):
        char = ""
        for item in self.items.all():
            char += "%s ; " % (item.name)
        return char


class Ingredient(models.Model):
    production          = models.ForeignKey("Production", on_delete=models.CASCADE)
    resource            = models.ForeignKey("Resource", on_delete=models.CASCADE)
    quantity            = models.IntegerField()
    
    def __str__(self):
        return f'{self.resource.name}'
    
    
class Production(models.Model):
    product             = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    date_of_production  = models.DateField()
    time_of_production  = models.TimeField()
    ingredients         = models.ManyToManyField(Ingredient, blank=True, related_name='used')
    output              = models.IntegerField(null=True, blank=True)
    production_id       = models.CharField(max_length=20, default=stamp, unique_for_date='date_of_production')
    
    def __str__(self):
        return f'{self.product} production - {self.production_id}'
    
    def used_resources_to_string(self):
        usage = ""
        for ing in self.ingredients.all():
            usage += '%s, ' % (ing.resource.name)
        return usage
    
    def add_usage(self, res):
        self.ingredients.add(res)
        self.save()


class Order_Item(models.Model):
    product             = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity            = models.IntegerField()
    invoice             = models.ForeignKey("Invoice", on_delete=models.DO_NOTHING)
    
    def __str__(self):
        return self.product.name

    def sub_total(self):
        return self.product.price * self.quantity
    

class Invoice(models.Model):
    number              = models.CharField(max_length=12, default=create_invoice_number)
    customer            = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    date_of_issue       = models.DateField(auto_now=True)
    time_of_issue       = models.TimeField(auto_now=True)
    items               = models.ManyToManyField(Order_Item, blank=True, related_name='items')
    date_of_payment     = models.DateField(blank=True, null=True)
    time_of_payment     = models.TimeField(blank=True, null=True)
    to_be_delivered     = models.BooleanField(default=False)
    delivery_cost       = models.FloatField(blank=True, null=True, default=fetch_settings()['delivery_fee'])
    
    def __str__(self):
        return self.number
    
    def add_item(self, item):
        self.items.add(item)
        self.save()
        
    def sub_total(self):
        amt = 0
        for item in self.items.all():
            amt += item.product.price * item.quantity
        return amt
        
    def total(self):
        if self.to_be_delivered:
            return self.delivery_cost + self.sub_total()
        return self.sub_total()

    def items_to_string(self):
        _list = ""
        for item in self.items.all():
            _list += f'{item.product.name} ({item.quantity} Bags), '
        return _list

    def count(self):
        cnt = 0
        for i in self.items.all():
            cnt += i.quantity
        return cnt
