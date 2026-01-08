from langchain_core.tools import tool
from django.db.models import Sum, Count, Q, F, FloatField
from django.db import models
from django.utils import timezone
from django.db.models.functions import TruncMonth

# App models
from store.models import Item, Category
from invoice.models import Invoice
from transactions.models import Sale, Purchase, SaleDetail
from bills.models import Bill
from accounts.models import Customer, Vendor

@tool
def get_today_sales() -> str:
    """Get sales summary for the current day."""
    today = timezone.now().date()
    
    # Filter sales for today
    sales = Sale.objects.filter(date_added__date=today)
    result = sales.aggregate(
        total=Sum('grand_total'),
        count=Count('id'),
        paid=Sum('amount_paid')
    )
    
    total = result['total'] or 0
    count = result['count'] or 0
    paid = result['paid'] or 0
    credit = total - paid
    
    if count == 0:
        return f"📊 مبيعات اليوم ({today}):\n\n🚫 لا توجد مبيعات مسجلة حتى الآن."
    
    return f"""📊 مبيعات اليوم ({today}):
━━━━━━━━━━━━━━━━
💰 الإجمالي: {total:,.0f} ريال
🧾 الفواتير: {count}
✅ المحصل: {paid:,.0f} ريال
⏳ الآجل: {credit:,.0f} ريال"""

@tool
def get_monthly_sales(month: int = None, year: int = None) -> str:
    """Get sales summary for a specific month and year."""
    now = timezone.now()
    month = month or now.month
    year = year or now.year
    
    sales = Sale.objects.filter(date_added__month=month, date_added__year=year)
    result = sales.aggregate(
        total=Sum('grand_total'),
        count=Count('id'),
        paid=Sum('amount_paid')
    )
    
    total = result['total'] or 0
    count = result['count'] or 0
    paid = result['paid'] or 0
    
    months_ar = ['يناير','فبراير','مارس','أبريل','مايو','يونيو',
                 'يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
    month_name = months_ar[month-1] if 1 <= month <= 12 else str(month)
    
    if count == 0:
        return f"📅 مبيعات {month_name} {year}:\n\n🚫 لا توجد مبيعات لهذا الشهر."
    
    return f"""📅 مبيعات {month_name} {year}:
━━━━━━━━━━━━━━━━
💰 الإجمالي: {total:,.0f} ريال
🧾 الفواتير: {count}
✅ المحصل: {paid:,.0f} ريال
⏳ الآجل: {total-paid:,.0f} ريال
69: 📊 متوسط اليوم: {total/30:,.0f} ريال"""

@tool
def get_yearly_sales(year: int = None) -> str:
    """Get sales summary for a full year with monthly breakdown."""
    now = timezone.now()
    year = year or now.year
    
    sales = Sale.objects.filter(date_added__year=year)
    result = sales.aggregate(
        total=Sum('grand_total'),
        count=Count('id'),
        paid=Sum('amount_paid')
    )
    
    total = result['total'] or 0
    count = result['count'] or 0
    paid = result['paid'] or 0
    
    if count == 0:
        return f"📅 مبيعات سنة {year}:\n\n🚫 لا توجد مبيعات مسجلة."
    
    # Monthly breakdown
    monthly = sales.annotate(
        month=TruncMonth('date_added')
    ).values('month').annotate(
        month_total=Sum('grand_total')
    ).order_by('month')
    
    months_ar = ['يناير','فبراير','مارس','أبريل','مايو','يونيو',
                 'يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر']
                 
    resp = f"""📅 مبيعات سنة {year}:
━━━━━━━━━━━━━━━━
💰 الإجمالي: {total:,.0f} ريال
🧾 الفواتير: {count}
✅ المحصل: {paid:,.0f} ريال
⏳ الآجل: {total-paid:,.0f} ريال

📈 التفصيل الشهري:
"""
    for m in monthly:
        m_num = m['month'].month
        resp += f"• {months_ar[m_num-1]}: {m['month_total']:,.0f} ريال\n"
    
    return resp

@tool
def get_financial_summary() -> str:
    """Get a comprehensive financial overview of the business."""
    today = timezone.now().date()
    
    # Sales
    today_sales = Sale.objects.filter(date_added__date=today).aggregate(total=Sum('grand_total'))['total'] or 0
    month_sales = Sale.objects.filter(date_added__month=today.month, date_added__year=today.year).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # Debts (Customers who haven't paid in full)
    customer_debts = Sale.objects.filter(amount_paid__lt=F('grand_total'))
    total_debts = customer_debts.aggregate(
        debt=Sum(F('grand_total') - F('amount_paid'), output_field=models.DecimalField(max_digits=12, decimal_places=2))
    )['debt'] or 0
    
    # Unpaid Bills
    unpaid_bills = Bill.objects.filter(status=False).aggregate(total=Sum('amount'))['total'] or 0
    
    # Stock Value (approx)
    # Optimized: DB aggregation instead of Python loop
    stock_value = Item.objects.aggregate(
        total_val=Sum(F('quantity') * F('price'), output_field=FloatField())
    )['total_val'] or 0
    
    return f"""📊 الملخص المالي العام
━━━━━━━━━━━━━━━━

💵 المبيعات:
• اليوم: {today_sales:,.0f} ريال
• الشهر: {month_sales:,.0f} ريال

💰 الذمم والالتزامات:
• مديونيات العملاء: {total_debts:,.0f} ريال
• فواتير غير مدفوعة: {unpaid_bills:,.0f} ريال

📦 المخزون:
• القيمة التقديرية: {stock_value:,.0f} ريال

📈 الرصيد الجاري المحتمل: {stock_value + total_debts - unpaid_bills:,.0f} ريال

━━━━━━━━━━━━━━━━
📆 {today}"""

@tool
def get_customer_invoices(customer_name: str) -> str:
    """Get all sales invoices for a specific customer."""
    customers = Customer.objects.filter(
        Q(first_name__icontains=customer_name) | Q(last_name__icontains=customer_name)
    )
    
    if not customers.exists():
        return f"❌ لم أجد عميل باسم: {customer_name}"
    
    customer = customers.first()
    sales = Sale.objects.filter(customer=customer).order_by('-date_added')[:10]
    
    if not sales.exists():
        return f"📋 لا توجد مبيعات مسجلة للعميل: {customer.get_full_name()}"
    
    lines = [f"📋 فواتير {customer.get_full_name()}:", "━━━━━━━━━━━━━━━━", ""]
    for s in sales:
        status = "✅ مدفوع" if s.amount_paid >= s.grand_total else "🔴 آجل"
        lines.append(f"{status} | {s.date_added.date()} | {s.grand_total:,.0f} ريال")
    
    return "\n".join(lines)

@tool
def get_low_stock_products(threshold: int = 10) -> str:
    """Identify products with low stock levels."""
    products = Item.objects.filter(quantity__lte=threshold).order_by('quantity')[:10]
    
    if not products.exists():
        return f"✅ جميع المنتجات متوفرة بمخزون جيد (أكثر من {threshold})."
    
    lines = ["⚠️ تحذير المخزون المنخفض:", "━━━━━━━━━━━━━━━━", ""]
    for p in products:
        emoji = "🔴" if p.quantity <= 3 else "🟡"
        lines.append(f"{emoji} {p.name}: المتبقي {p.quantity} قطعة")
    
    return "\n".join(lines)

@tool
def get_top_selling_products(limit: int = 5) -> str:
    """Get the most sold products based on quantity in the current month."""
    now = timezone.now()
    
    results = SaleDetail.objects.filter(
        sale__date_added__month=now.month,
        sale__date_added__year=now.year
    ).values('item__name').annotate(
        total_qty=Sum('quantity'),
        total_revenue=Sum('total_detail')
    ).order_by('-total_qty')[:limit]
    
    if not results:
        return "🚫 لا توجد بيانات مبيعات كافية لهذا الشهر."
    
    lines = ["🏆 الأكثر مبيعاً هذا الشهر:", "━━━━━━━━━━━━━━━━", ""]
    medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣']
    
    for i, res in enumerate(results):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        lines.append(f"{medal} {res['item__name']}")
        lines.append(f"   📦 الكمية: {res['total_qty']} | 💰 الإيراد: {res['total_revenue']:,.0f} ريال")
        lines.append("")
    
    return "\n".join(lines)

@tool
def get_best_customers(limit: int = 5) -> str:
    """Get top customers based on total spending."""
    results = Sale.objects.values('customer__first_name', 'customer__last_name', 'customer__loyalty_points').annotate(
        total_spent=Sum('grand_total'),
        invoice_count=Count('id')
    ).order_by('-total_spent')[:limit]
    
    if not results:
        return "🚫 لا توجد بيانات عملاء كافية."
    
    lines = ["💎 أكثر العملاء شراءً:", "━━━━━━━━━━━━━━━━", ""]
    for i, res in enumerate(results):
        name = f"{res['customer__first_name']} {res['customer__last_name'] or ''}"
        lines.append(f"{i+1}. {name}")
        lines.append(f"   💰 إجمالي المشتريات: {res['total_spent']:,.0f} ريال | 🧾 فواتير: {res['invoice_count']}")
        lines.append(f"   🌟 نقاط الولاء: {res['customer__loyalty_points']}")
        lines.append("")
        
    return "\n".join(lines)

@tool
def get_all_customers() -> str:
    """List all customers with their loyalty points."""
    customers = Customer.objects.all().order_by('-loyalty_points')[:50] # Limit to 50 to avoid overflow
    
    if not customers.exists():
        return "🚫 لا يوجد عملاء مسجلين."
    
    lines = ["👥 قائمة العملاء ونقاط الولاء:", "━━━━━━━━━━━━━━━━"]
    for c in customers:
        lines.append(f"👤 {c.get_full_name()}")
        lines.append(f"   🌟 نقاط الولاء: {c.loyalty_points}")
        lines.append("   ─ ─ ─")
    
    if Customer.objects.count() > 50:
        lines.append("\n⚠️ تم عرض أول 50 عميل فقط.")
    return "\n".join(lines)

@tool
def search_item(query: str) -> str:
    """Search for an item by name and return its details."""
    items = Item.objects.filter(name__icontains=query)
    if not items.exists():
        return f"🚫 لم يتم العثور على منتج يطابق '{query}'."
    
    lines = [f"🔍 نتائج البحث عن '{query}':", "━━━━━━━━━━━━━━━━"]
    for item in items:
        lines.append(f"📦 {item.name}")
        lines.append(f"   💰 السعر: {item.price:,.0f} ريال")
        lines.append(f"   🔢 المخزون: {item.quantity} قطعة")
        lines.append(f"   📝 الوصف: {item.description or 'لا يوجد'}")
        lines.append("")
    
    return "\n".join(lines)

@tool
def get_categories() -> str:
    """List all product categories."""
    categories = Category.objects.all()
    if not categories.exists():
        return "🚫 لا توجد أقسام مسجلة."
    
    lines = ["📁 الأقسام المتوفرة:", "━━━━━━━━━━━━━━━━"]
    for cat in categories:
        count = Item.objects.filter(category=cat).count()
        lines.append(f"🔹 {cat.name} ({count} منتج)")
    
    return "\n".join(lines)

@tool
def get_vendors() -> str:
    """List all vendors/suppliers."""
    vendors = Vendor.objects.all()
    if not vendors.exists():
        return "🚫 لا يوجد موردون مسجلون."
    
    lines = ["🤝 الموردون:", "━━━━━━━━━━━━━━━━"]
    for v in vendors:
        lines.append(f"🏢 {v.name}")
        if v.phone_number: lines.append(f"   📞 {v.phone_number}")
    
    return "\n".join(lines)

@tool
def get_unpaid_bills() -> str:
    """List all unpaid bills."""
    bills = Bill.objects.filter(status=False)
    if not bills.exists():
        return "✅ لا توجد فواتير غير مدفوعة حالياً."
    
    total = bills.aggregate(total=Sum('amount'))['total'] or 0
    lines = [f"💸 الفواتير غير المدفوعة (إجمالي: {total:,.0f} ريال):", "━━━━━━━━━━━━━━━━"]
    for b in bills:
        lines.append(f"🧾 {b.institution_name}: {b.amount:,.0f} ريال")
        lines.append(f"   📝 {b.description or 'بدون وصف'}")
    
    return "\n".join(lines)

@tool
def create_purchase_order(item_name: str, vendor_name: str, quantity: int, price_per_item: float, description: str = "") -> str:
    """Create a new purchase order for restocking inventory.
    
    Args:
        item_name: Name of the item to purchase
        vendor_name: Name of the vendor/supplier
        quantity: Quantity to order
        price_per_item: Price per item unit
        description: Optional description for the purchase order
    """
    try:
        # Find the item
        items = Item.objects.filter(name__icontains=item_name)
        if not items.exists():
            return f"❌ لم يتم العثور على منتج باسم: {item_name}"
        item = items.first()
        
        # Find the vendor
        vendors = Vendor.objects.filter(name__icontains=vendor_name)
        if not vendors.exists():
            return f"❌ لم يتم العثور على مورد باسم: {vendor_name}"
        vendor = vendors.first()
        
        # Create purchase order
        purchase = Purchase.objects.create(
            item=item,
            vendor=vendor,
            quantity=quantity,
            price=price_per_item,
            description=description,
            total_value=quantity * price_per_item
        )
        
        return f"""✅ تم إنشاء طلب الشراء بنجاح!
━━━━━━━━━━━━━━━━
📦 المنتج: {item.name}
🏢 المورد: {vendor.name}
🔢 الكمية: {quantity}
💰 السعر للوحدة: {price_per_item:,.2f} ريال
💵 الإجمالي: {purchase.total_value:,.2f} ريال
📝 الوصف: {description or 'لا يوجد'}
📅 تاريخ الطلب: {purchase.order_date.strftime('%Y-%m-%d %H:%M')}
🚚 حالة التوصيل: قيد الانتظار

رقم الطلب: #{purchase.id}"""
    except Exception as e:
        return f"❌ حدث خطأ أثناء إنشاء طلب الشراء: {str(e)}"

@tool
def create_sale(customer_name: str, items_data: str) -> str:
    """Create a new sale transaction.
    
    Args:
        customer_name: Name of the customer (first name or full name)
        items_data: Items to sell in format: "item_name:quantity:price, item_name:quantity:price"
                   Example: "قلم:5:10, دفتر:2:25"
    
    Note: This creates a basic sale. For complex sales with tax, use the web interface.
    """
    try:
        # Find customer
        customers = Customer.objects.filter(
            Q(first_name__icontains=customer_name) | Q(last_name__icontains=customer_name)
        )
        if not customers.exists():
            return f"❌ لم يتم العثور على عميل باسم: {customer_name}\n💡 استخدم create_customer لإضافة عميل جديد"
        customer = customers.first()
        
        # Parse items
        items_list = []
        total = 0
        
        for item_str in items_data.split(','):
            parts = item_str.strip().split(':')
            if len(parts) != 3:
                return f"❌ صيغة خاطئة للمنتجات. استخدم: اسم_المنتج:الكمية:السعر"
            
            item_name, qty, price = parts[0].strip(), int(parts[1].strip()), float(parts[2].strip())
            
            # Find item
            items = Item.objects.filter(name__icontains=item_name)
            if not items.exists():
                return f"❌ لم يتم العثور على منتج: {item_name}"
            item = items.first()
            
            # Check stock
            if item.quantity < qty:
                return f"⚠️ مخزون غير كافٍ لـ {item.name}. المتوفر: {item.quantity}"
            
            items_list.append({
                'item': item,
                'quantity': qty,
                'price': price,
                'total': qty * price
            })
            total += qty * price
        
        # Create sale
        sale = Sale.objects.create(
            customer=customer,
            sub_total=total,
            grand_total=total,
            tax_amount=0,
            tax_percentage=0,
            amount_paid=0,
            amount_change=0
        )
        
        # Create sale details and update stock
        for item_data in items_list:
            SaleDetail.objects.create(
                sale=sale,
                item=item_data['item'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                total_detail=item_data['total']
            )
            # Update stock
            item_data['item'].quantity -= item_data['quantity']
            item_data['item'].save()
        
        lines = [
            "✅ تم إنشاء فاتورة البيع بنجاح!",
            "━━━━━━━━━━━━━━━━",
            f"👤 العميل: {customer.get_full_name()}",
            f"📅 التاريخ: {sale.date_added.strftime('%Y-%m-%d %H:%M')}",
            "",
            "📦 المنتجات:"
        ]
        
        for item_data in items_list:
            lines.append(f"  • {item_data['item'].name}: {item_data['quantity']} × {item_data['price']:,.2f} = {item_data['total']:,.2f} ريال")
        
        lines.extend([
            "",
            f"💰 الإجمالي: {total:,.2f} ريال",
            f"⏳ المبلغ المدفوع: 0 ريال (آجل)",
            "",
            f"رقم الفاتورة: #{sale.id}"
        ])
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ حدث خطأ أثناء إنشاء الفاتورة: {str(e)}"

@tool
def create_customer(first_name: str, last_name: str = "", phone: str = "", email: str = "", address: str = "") -> str:
    """Create a new customer in the system.
    
    Args:
        first_name: Customer's first name (required)
        last_name: Customer's last name (optional)
        phone: Customer's phone number (optional)
        email: Customer's email address (optional)
        address: Customer's address (optional)
    """
    try:
        # Check if customer already exists
        existing = Customer.objects.filter(
            first_name__iexact=first_name,
            last_name__iexact=last_name
        )
        if existing.exists():
            return f"⚠️ العميل '{first_name} {last_name}' موجود مسبقاً في النظام"
        
        customer = Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            address=address,
            loyalty_points=0
        )
        
        return f"""✅ تم إضافة العميل بنجاح!
━━━━━━━━━━━━━━━━
👤 الاسم: {customer.get_full_name()}
📞 الهاتف: {phone or 'غير محدد'}
📧 البريد: {email or 'غير محدد'}
📍 العنوان: {address or 'غير محدد'}
🌟 نقاط الولاء: 0

رقم العميل: #{customer.id}"""
    except Exception as e:
        return f"❌ حدث خطأ أثناء إضافة العميل: {str(e)}"

@tool
def search_customer(query: str) -> str:
    """Search for customers by name or phone number.
    
    Args:
        query: Search term (name or phone number)
    """
    customers = Customer.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(phone__icontains=query)
    )[:10]
    
    if not customers.exists():
        return f"❌ لم يتم العثور على عملاء يطابقون: {query}"
    
    lines = [f"🔍 نتائج البحث عن '{query}':", "━━━━━━━━━━━━━━━━", ""]
    for c in customers:
        lines.append(f"👤 {c.get_full_name()}")
        lines.append(f"   📞 {c.phone or 'لا يوجد'}")
        lines.append(f"   🌟 نقاط الولاء: {c.loyalty_points}")
        lines.append(f"   🆔 رقم العميل: #{c.id}")
        lines.append("   ─ ─ ─")
    
    if Customer.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(phone__icontains=query)
    ).count() > 10:
        lines.append("\n⚠️ تم عرض أول 10 نتائج فقط.")
    
    return "\n".join(lines)

@tool
def get_customer_details(customer_name: str) -> str:
    """Get detailed information about a customer including purchase history.
    
    Args:
        customer_name: Customer's name (first or last name)
    """
    customers = Customer.objects.filter(
        Q(first_name__icontains=customer_name) | Q(last_name__icontains=customer_name)
    )
    
    if not customers.exists():
        return f"❌ لم يتم العثور على عميل باسم: {customer_name}"
    
    customer = customers.first()
    
    # Get sales statistics
    sales = Sale.objects.filter(customer=customer)
    total_sales = sales.aggregate(
        total=Sum('grand_total'),
        paid=Sum('amount_paid'),
        count=Count('id')
    )
    
    total = total_sales['total'] or 0
    paid = total_sales['paid'] or 0
    count = total_sales['count'] or 0
    debt = total - paid
    
    lines = [
        f"👤 معلومات العميل: {customer.get_full_name()}",
        "━━━━━━━━━━━━━━━━",
        "",
        "📋 البيانات الأساسية:",
        f"   🆔 رقم العميل: #{customer.id}",
        f"   📞 الهاتف: {customer.phone or 'غير محدد'}",
        f"   📧 البريد: {customer.email or 'غير محدد'}",
        f"   📍 العنوان: {customer.address or 'غير محدد'}",
        f"   🌟 نقاط الولاء: {customer.loyalty_points}",
        "",
        "💰 الإحصائيات المالية:",
        f"   🧾 عدد الفواتير: {count}",
        f"   💵 إجمالي المشتريات: {total:,.2f} ريال",
        f"   ✅ المدفوع: {paid:,.2f} ريال",
        f"   ⏳ المتبقي (الآجل): {debt:,.2f} ريال"
    ]
    
    # Add recent sales
    recent_sales = sales.order_by('-date_added')[:5]
    if recent_sales.exists():
        lines.extend(["", "📊 آخر 5 فواتير:"])
        for s in recent_sales:
            status = "✅" if s.amount_paid >= s.grand_total else "⏳"
            lines.append(f"   {status} {s.date_added.strftime('%Y-%m-%d')} | {s.grand_total:,.2f} ريال")
    
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════
# User Preferences Management Tools
# ═══════════════════════════════════════════════════════════════

@tool
def get_user_preferences(phone_number: str) -> str:
    """Get current user preferences for display format and pagination.
    
    Args:
        phone_number: User's phone number
    """
    from integration.models import UserPreferences
    
    try:
        prefs = UserPreferences.objects.get(phone_number=phone_number)
        
        format_display = {
            'auto': 'تلقائي (يختار النظام الأنسب)',
            'text': 'نص (عرض نصي بسيط)',
            'table': 'جدول (جداول منسقة)',
            'paginated': 'صفحات (عرض بصفحات)',
            'summary': 'ملخص (ملخص مختصر)'
        }
        
        return f"""⚙️ إعداداتك الحالية:
━━━━━━━━━━━━━━━━

📊 طريقة العرض: {format_display.get(prefs.preferred_format, prefs.preferred_format)}
📄 عدد العناصر في الصفحة: {prefs.max_items_per_page}
🌐 اللغة: {'العربية' if prefs.language == 'ar' else 'English'}

💡 لتغيير الإعدادات:
• "غير طريقة العرض إلى جدول"
• "غير عدد العناصر إلى 15"

📅 آخر تحديث: {prefs.updated_at.strftime('%Y-%m-%d %H:%M')}"""
        
    except UserPreferences.DoesNotExist:
        return """⚙️ إعداداتك:
━━━━━━━━━━━━━━━━

📊 طريقة العرض: تلقائي (افتراضي)
📄 عدد العناصر في الصفحة: 10 (افتراضي)

💡 يمكنك تخصيص الإعدادات:
• "غير طريقة العرض إلى جدول"
• "غير طريقة العرض إلى نص"
• "غير طريقة العرض إلى صفحات"
• "غير عدد العناصر إلى 15"

سيتم حفظ اختياراتك للمرات القادمة! 🎯"""

@tool
def set_display_format(phone_number: str, format_type: str) -> str:
    """Set user's preferred display format.
    
    Args:
        phone_number: User's phone number
        format_type: Display format (auto/text/table/paginated/summary)
    """
    from integration.models import UserPreferences
    
    # Normalize format type
    format_map = {
        'تلقائي': 'auto',
        'نص': 'text',
        'جدول': 'table',
        'صفحات': 'paginated',
        'ملخص': 'summary',
        'auto': 'auto',
        'text': 'text',
        'table': 'table',
        'paginated': 'paginated',
        'summary': 'summary'
    }
    
    normalized_format = format_map.get(format_type.lower())
    
    if not normalized_format:
        return f"""❌ طريقة عرض غير صحيحة: {format_type}

الخيارات المتاحة:
• تلقائي (auto) - يختار النظام الأنسب
• نص (text) - عرض نصي بسيط
• جدول (table) - جداول منسقة
• صفحات (paginated) - عرض بصفحات
• ملخص (summary) - ملخص مختصر

مثال: "غير طريقة العرض إلى جدول" """
    
    try:
        prefs, created = UserPreferences.objects.get_or_create(
            phone_number=phone_number,
            defaults={'preferred_format': normalized_format}
        )
        
        if not created:
            prefs.preferred_format = normalized_format
            prefs.save()
        
        format_display = {
            'auto': 'تلقائي',
            'text': 'نص',
            'table': 'جدول',
            'paginated': 'صفحات',
            'summary': 'ملخص'
        }
        
        action = "تم حفظ" if created else "تم تحديث"
        
        return f"""✅ {action} إعداداتك بنجاح!

📊 طريقة العرض الجديدة: {format_display[normalized_format]}

من الآن فصاعداً، سأعرض لك البيانات بهذه الطريقة تلقائياً 🎯

💡 يمكنك تغيير الإعدادات في أي وقت!"""
        
    except Exception as e:
        return f"❌ حدث خطأ أثناء حفظ الإعدادات: {str(e)}"

@tool
def set_items_per_page(phone_number: str, items_count: int) -> str:
    """Set user's preferred number of items per page.
    
    Args:
        phone_number: User's phone number
        items_count: Number of items per page (5-50)
    """
    from integration.models import UserPreferences
    
    if items_count < 5 or items_count > 50:
        return """❌ العدد يجب أن يكون بين 5 و 50

مثال: "غير عدد العناصر إلى 10" """
    
    try:
        prefs, created = UserPreferences.objects.get_or_create(
            phone_number=phone_number,
            defaults={'max_items_per_page': items_count}
        )
        
        if not created:
            prefs.max_items_per_page = items_count
            prefs.save()
        
        action = "تم حفظ" if created else "تم تحديث"
        
        return f"""✅ {action} إعداداتك بنجاح!

📄 عدد العناصر في الصفحة: {items_count}

من الآن فصاعداً، سأعرض {items_count} عنصر في كل صفحة 📋

💡 يمكنك تغيير هذا الرقم في أي وقت!"""
        
    except Exception as e:
        return f"❌ حدث خطأ أثناء حفظ الإعدادات: {str(e)}"


# ═══════════════════════════════════════════════════════════════
# Smart Tools for Multi-Step Operations
# ═══════════════════════════════════════════════════════════════

@tool
def manage_purchase_order(
    phone_number: str,
    item_name: str = None,
    vendor_name: str = None,
    quantity: int = None,
    price_per_item: float = None,
    description: str = "",
    reset: bool = False
) -> str:
    """
    Smart tool for creating purchase orders with multi-step support.
    Use this whenever a user wants to buy something or create a PO.
    It can handle partial information and will prompt for missing details.
    
    Args:
        phone_number: User's phone number (required for context)
        item_name: Name of the item
        vendor_name: Name of the vendor
        quantity: Number of items
        price_per_item: Price per single item
        description: Optional description
        reset: If True, clears any existing pending operation for this user
    """
    from integration.models import PendingOperation
    
    # 1. Handle Reset
    if reset:
        PendingOperation.objects.filter(
            phone_number=phone_number, 
            operation_type='purchase_order'
        ).delete()
        return "✅ تم إلغاء العملية السابقة. كيف يمكنني مساعدتك الآن؟"

    # 2. Get or Create Pending Operation
    op, created = PendingOperation.objects.get_or_create(
        phone_number=phone_number,
        operation_type='purchase_order',
        defaults={'data': {}}
    )
    
    current_data = op.data
    
    # 3. Update Data with new inputs
    # Only update if value is provided (not None)
    if item_name: current_data['item_name'] = item_name
    if vendor_name: current_data['vendor_name'] = vendor_name
    if quantity: current_data['quantity'] = quantity
    if price_per_item: current_data['price_per_item'] = price_per_item
    if description: current_data['description'] = description
    
    op.data = current_data
    op.save()
    
    # 4. Check for Missing Fields
    required_fields = {
        'item_name': 'اسم المنتج',
        'vendor_name': 'اسم المورد',
        'quantity': 'الكمية المطلوبة',
        'price_per_item': 'سعر الحبة الواحدة'
    }
    
    missing = []
    for field, label in required_fields.items():
        if field not in current_data or not current_data[field]:
            missing.append(label)
    
    # 5. Determine Response
    if missing:
        # Construct summary of what we have
        summary_lines = []
        if current_data.get('item_name'): summary_lines.append(f"📦 المنتج: {current_data['item_name']}")
        if current_data.get('vendor_name'): summary_lines.append(f"🏢 المورد: {current_data['vendor_name']}")
        if current_data.get('quantity'): summary_lines.append(f"🔢 الكمية: {current_data['quantity']}")
        if current_data.get('price_per_item'): summary_lines.append(f"💰 السعر: {current_data['price_per_item']}")
        
        summary_text = "\n".join(summary_lines)
        
        # Ask for the first missing item
        next_needed = missing[0]
        
        response = f"""📝 جاري تسجيل طلب الشراء...
━━━━━━━━━━━━━━━━
{summary_text}

❓ أحتاج إلى معرفة **{next_needed}** لإكمال الطلب.
"""
        return response

    # 6. All Data Present -> Execute Creation
    try:
        result = create_purchase_order(
            item_name=current_data['item_name'],
            vendor_name=current_data['vendor_name'],
            quantity=int(current_data['quantity']),
            price_per_item=float(current_data['price_per_item']),
            description=current_data.get('description', "")
        )
        
        # Cleanup on success
        op.delete()
        
        return result
        
    except Exception as e:
        return f"❌ حدث خطأ أثناء إنشاء الطلب: {str(e)}"

@tool
def manage_sale(
    phone_number: str,
    customer_name: str = None,
    item_input: str = None, # format: "name:qty:price"
    reset: bool = False
) -> str:
    """
    Smart tool for creating sales with multi-step support.
    Handles adding items incrementally to a sale.
    
    Args:
        phone_number: User's phone number
        customer_name: Name of the customer
        item_input: Item details in format "name:qty:price" (e.g., "pen:5:10")
        reset: If True, clears the current pending sale
    """
    from integration.models import PendingOperation
    
    # 1. Handle Reset
    if reset:
        PendingOperation.objects.filter(
            phone_number=phone_number, 
            operation_type='sale'
        ).delete()
        return "✅ تم إلغاء عملية البيع السابقة. كيف يمكنني مساعدتك الآن؟"

    # 2. Get or Create Pending Operation
    op, created = PendingOperation.objects.get_or_create(
        phone_number=phone_number,
        operation_type='sale',
        defaults={'data': {'items': []}}
    )
    
    current_data = op.data
    if 'items' not in current_data:
        current_data['items'] = []
        
    # 3. Update Data
    if customer_name:
        current_data['customer_name'] = customer_name
        
    if item_input:
        try:
            parts = item_input.split(':')
            item_entry = {'name': parts[0].strip()}
            if len(parts) > 1: item_entry['qty'] = int(parts[1])
            if len(parts) > 2: item_entry['price'] = float(parts[2])
            
            # Add to items list
            current_data['items'].append(item_entry)
        except:
            return "⚠️ تنسيق المنتج غير صحيح. يرجى استخدامه كـ 'اسم:كمية:سعر'"

    op.data = current_data
    op.save()
    
    # 4. Check status
    missing = []
    if 'customer_name' not in current_data:
        missing.append("اسم العميل")
        
    items = current_data.get('items', [])
    
    # 5. Check if any item in list is incomplete
    incomplete_items = []
    for i, item in enumerate(items):
        if 'qty' not in item or 'price' not in item:
            incomplete_items.append(item['name'])
            
    # 6. Determine Response
    
    # Provide summary of current cart
    summary_lines = []
    if current_data.get('customer_name'):
        summary_lines.append(f"👤 العميل: {current_data['customer_name']}")
        
    if items:
        summary_lines.append("\n🛒 السلة:")
        for item in items:
            details = f"{item['name']}"
            if 'qty' in item: details += f" (x{item['qty']})"
            if 'price' in item: details += f" بسعر {item['price']}"
            if 'qty' not in item or 'price' not in item: details += " ⚠️ بيانات ناقصة"
            summary_lines.append(f"   - {details}")
            
    summary_text = "\n".join(summary_lines)

    # Priority 1: Missing Customer Name
    if 'customer_name' not in current_data:
        return f"""📝 فاتورة بيع جديدة
━━━━━━━━━━━━━━━━
{summary_text if summary_text else ''}

❓ من هو **العميل**؟"""

    # Priority 2: Incomplete Items
    if incomplete_items:
        next_item = incomplete_items[0]
        return f"""📝 متابعة الفاتورة...
━━━━━━━━━━━━━━━━
{summary_text}

❓ بالنسبة للمنتج **{next_item}**، كم الكمية والسعر؟"""
        
    # Priority 3: No Items
    if not items:
        return f"""📝 فاتورة بيع لـ {current_data['customer_name']}
━━━━━━━━━━━━━━━━

❓ ماذا يريد أن يشتري؟ (اسم المنتج والكمية والسعر)"""

    return f"""📝 ملخص الفاتورة الحالية:
━━━━━━━━━━━━━━━━
{summary_text}

✏️ لإضافة المزيد: "أضف دفتر 5 حبات بـ 10 ريال"
✅ للإتمام: قل "اعتمد الفاتورة" أو "تم"
❌ للإلغاء: قل "إلغاء الأمر"
"""

@tool
def finalize_sale(phone_number: str) -> str:
    """
    Finalizes and creates the sale transaction from the pending items.
    """
    from integration.models import PendingOperation
    
    try:
        op = PendingOperation.objects.get(
            phone_number=phone_number, 
            operation_type='sale'
        )
        data = op.data
        
        if 'customer_name' not in data or not data.get('items'):
            return "❌ لا توجد بيانات كافية لإتمام البيع."
            
        # Construct items_data string: "name:qty:price, name:qty:price"
        items_str_list = []
        for item in data['items']:
            if 'qty' not in item or 'price' not in item:
                return f"⚠️ بيانات ناقصة للمنتج {item['name']}"
            items_str_list.append(f"{item['name']}:{item['qty']}:{item['price']}")
            
        items_data_str = ", ".join(items_str_list)
        
        # Execute
        result = create_sale(data['customer_name'], items_data_str)
        
        # Cleanup
        op.delete()
        
        return result
        
    except PendingOperation.DoesNotExist:
        return "❌ لا توجد عملية بيع معلقة."

