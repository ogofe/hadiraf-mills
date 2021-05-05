from django.urls import path
from .views import (
    Overview_Page, Metrics_Page, Login_Page,
    Production_Page, Create_Production_Page, Production_Detail_Page,
    Invoices_Page, Create_Invoice_Page, Invoice_Detail_Page,
    Customers_Page,  Add_Customer_Page,
    Staff_Page, Create_Staff_Page,
    Resources_Page, Create_Resource_Page,
    Products_Page, Create_Product_Page,
    Shipments_Page, Create_Shipment_Page, Shipment_Detail_Page,
    sign_out, set_production_output,
)

app_name = 'work' 

urlpatterns = [
    path('', Overview_Page.as_view(), name='overview'),
    path('login/', Login_Page.as_view(), name='login'),
    path('logout/', sign_out, name='sign-out'),
    
    path('customers/', Customers_Page.as_view(), name='customers'),
    path('customers/add/', Add_Customer_Page.as_view(), name='add-customer'),
    
    path('invoices/', Invoices_Page.as_view(), name='invoices'),
    path('invoices/add/', Create_Invoice_Page.as_view(), name='add-invoice'),
    path('invoices/<str:invoice>/', Invoice_Detail_Page.as_view(), name='invoice-view'),
    
    path('products/', Products_Page.as_view(), name='products'),
    path('products/add/', Create_Product_Page.as_view(), name='add-product'),

    path('resources/', Resources_Page.as_view(), name='resources'),
    path('resources/add/', Create_Resource_Page.as_view(), name='add-resource'),
    
    path('shipments/', Shipments_Page.as_view(), name='shipments'),
    path('shipments/add/', Create_Shipment_Page.as_view(), name='add-shipment'),
    path('shipments/<str:shipment>/', Shipment_Detail_Page.as_view(), name='shipment-view'),
    
    path('production/', Production_Page.as_view(), name='production'),
    path('production/add/', Create_Production_Page.as_view(), name='add-production'),
    path('production/<str:cycle>/set-output/', set_production_output, name='set-output'),
    path('production/<str:production_id>/', Production_Detail_Page.as_view(), name='production-view'),
    
    path('metrics/', Metrics_Page.as_view(), name='metrics'),

    path('staff/', Staff_Page.as_view(), name='staff'),
    path('staff/add/', Create_Staff_Page.as_view(), name='add-staff'),
]
