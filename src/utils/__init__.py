import json, os
from django.conf import settings
from .errors import SettingNotFoundError

# from xlsxwriter import worksheet, Workbook, chart_line
# from openpyxl.workbook import web, views, interface

def fetch_settings():
    filename, content = os.path.join(settings.BASE_DIR, 'settings.json'), {}
    with open(filename, 'r') as file:
        content = json.load(file)
    return content

def alter_setting(setting, change):
    filename, content = os.path.join(settings.BASE_DIR, 'settings.json'), fetch_settings()
    if setting in content:
        content[setting] = change
        with open(filename, 'w') as file:
            json.dump(content, file)
        return True
    raise SettingNotFoundError
    
    
# def create_spreadsheet(data:dict):
#     book = Workbook(date.get(title, options={'in_memory': True}))
#     sheet = worksheet.Worksheet()
#     sheet.name = data['title']
#     sheet.add_table()
#     sheet.activate()
#     for i in range(0, len(data['data'])):
#         sheet.write_row(i, 0, data['data'][i])
#     sheet.set_header(data['title'])
#     book.add_worksheet(sheet)
#     book.close()
    
def get_dataset(query, date=None):
    from factory.models import Production, Resource, Expense, Invoice
    dataset = []
    if query == 'production':
        qs = Production.objects.all()
        dataset.append([str(cycle.date_of_production),
                        str(cycle.time_of_production),
                        cycle.product.name,
                        cycle.output,
                        cycle.used_resources_to_string()] for cycle in qs)
    elif query == 'inventory':
        qs = Resource.objects.all()
        dataset.append([
            res.name,
            res.quantity,
            res.date_received,
            res.time_received,
            res.reveived_from
        ] for res in qs)
    elif query == 'sales':
        qs = Invoice.objects.all()
        dataset.append([
            order.number,
            str(order.date_of_issue),
            str(order.time_of_issue),
            order.customer.name(),
            order.items_to_string(),
            order.total(),
            order.date_of_payment,
            order.time_of_payment,
        ] for order in qs)
    return dataset



class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

