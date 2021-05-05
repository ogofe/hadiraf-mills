from django.contrib import admin
from .models import (
    Customer,
    Invoice,
    Order_Item,
    Product,
    Production,
    Ingredient,
    Resource,
    Shipment,
    Worker
)

admin.site.site_header = "Hadiraf Farms"
admin.site.index_title = "Admin Panel"
admin.site.site_title = "Hadiraf Farms"

admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(Order_Item)
admin.site.register(Product)
admin.site.register(Production)
admin.site.register(Ingredient)
admin.site.register(Resource)
admin.site.register(Shipment)
admin.site.register(Worker)