import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from store.models import Category, Item
from accounts.models import Vendor, Customer
from transactions.models import Sale, SaleDetail, Purchase
from invoice.models import Invoice
from bills.models import Bill

class Command(BaseCommand):
    help = 'Initialize the system with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Initializing sample data...')

        # 1. Categories
        categories_names = ['Electronics', 'Groceries', 'Clothing', 'Furniture', 'Beauty']
        categories = []
        for name in categories_names:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        # 2. Vendors
        vendors_data = [
            {'name': 'TechSupplies Inc', 'phone_number': 123456789, 'address': '123 Tech Ave'},
            {'name': 'FreshFood Co', 'phone_number': 987654321, 'address': '456 Farm Road'},
            {'name': 'StyleHub', 'phone_number': 456789123, 'address': '789 Fashion St'},
        ]
        vendors = []
        for data in vendors_data:
            vendor, created = Vendor.objects.get_or_create(**data)
            vendors.append(vendor)
        self.stdout.write(self.style.SUCCESS(f'Created {len(vendors)} vendors'))

        # 3. Customers
        customers_data = [
            {'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com', 'phone': '0112233445'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com', 'phone': '0556677889'},
            {'first_name': 'Ahmed', 'last_name': 'Ali', 'email': 'ahmed@example.com', 'phone': '0998877665'},
        ]
        customers = []
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(**data)
            customers.append(customer)
        self.stdout.write(self.style.SUCCESS(f'Created {len(customers)} customers'))

        # 4. Items
        items_data = [
            {'name': 'Laptop', 'description': 'High performance laptop', 'category': categories[0], 'quantity': 10, 'price': 3500, 'vendor': vendors[0]},
            {'name': 'Smartphone', 'description': 'Latest smartphone', 'category': categories[0], 'quantity': 25, 'price': 1500, 'vendor': vendors[0]},
            {'name': 'Bread', 'description': 'Freshly baked bread', 'category': categories[1], 'quantity': 50, 'price': 2.5, 'vendor': vendors[1]},
            {'name': 'Milk', 'description': 'Organic milk', 'category': categories[1], 'quantity': 40, 'price': 1.5, 'vendor': vendors[1]},
            {'name': 'T-Shirt', 'description': 'Cotton t-shirt', 'category': categories[2], 'quantity': 100, 'price': 15, 'vendor': vendors[2]},
        ]
        items = []
        for data in items_data:
            item, created = Item.objects.get_or_create(name=data['name'], defaults=data)
            items.append(item)
        self.stdout.write(self.style.SUCCESS(f'Created {len(items)} items'))

        # 5. Purchases
        for item in items:
            Purchase.objects.create(
                item=item,
                description=f'Initial purchase of {item.name}',
                vendor=item.vendor,
                quantity=item.quantity,
                delivery_status='S',
                price=item.price * 0.7,
                total_value=item.quantity * item.price * 0.7
            )
        self.stdout.write(self.style.SUCCESS('Created sample purchases'))

        # 6. Sales & SaleDetails
        for i in range(10):
            customer = random.choice(customers)
            sale = Sale.objects.create(
                customer=customer,
                sub_total=0,
                grand_total=0,
                tax_amount=0,
                tax_percentage=15,
                amount_paid=0,
                amount_change=0
            )
            
            total_sale = 0
            for _ in range(random.randint(1, 3)):
                item = random.choice(items)
                qty = random.randint(1, 5)
                price = item.price
                total_detail = price * qty
                
                SaleDetail.objects.create(
                    sale=sale,
                    item=item,
                    price=price,
                    quantity=qty,
                    total_detail=total_detail
                )
                total_sale += total_detail
            
            sale.sub_total = total_sale
            sale.tax_amount = total_sale * 0.15
            sale.grand_total = total_sale + sale.tax_amount
            sale.amount_paid = sale.grand_total
            sale.save()
            
        self.stdout.write(self.style.SUCCESS('Created sample sales'))

        # 7. Invoices
        for _ in range(5):
            item = random.choice(items)
            Invoice.objects.create(
                customer_name=random.choice(['Abdi', 'Fatuma', 'Musa']),
                contact_number='254712345678',
                item=item,
                price_per_item=item.price,
                quantity=random.randint(1, 4),
                shipping=50,
            )
        self.stdout.write(self.style.SUCCESS('Created sample invoices'))

        # 8. Bills
        bills_data = [
            {'institution_name': 'KPL', 'amount': 1500, 'description': 'Electricity Bill', 'payment_details': 'Mpesa Paybill 888888', 'status': True},
            {'institution_name': 'Water Co', 'amount': 450, 'description': 'Water Bill', 'payment_details': 'Mpesa Paybill 999999', 'status': False},
        ]
        for data in bills_data:
            Bill.objects.create(**data)
        self.stdout.write(self.style.SUCCESS('Created sample bills'))

        self.stdout.write(self.style.SUCCESS('Sample data initialization complete!'))
