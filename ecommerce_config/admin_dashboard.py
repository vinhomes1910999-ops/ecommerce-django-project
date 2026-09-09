from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from products.models import Product


@staff_member_required
def dashboard_stats(request):
    """API nội bộ trả về dữ liệu JSON cho biểu đồ trên trang admin."""
    today = timezone.now().date()
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

    revenue_by_day = []
    for day in last_7_days:
        total = Order.objects.filter(
            created_at__date=day, status__in=['completed', 'shipping', 'confirmed']
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        revenue_by_day.append(float(total))

    orders_by_status = list(
        Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    )

    top_products = list(
        Product.objects.order_by('-sold_count')[:5].values('name', 'sold_count')
    )

    return JsonResponse({
        'labels': [d.strftime('%d/%m') for d in last_7_days],
        'revenue': revenue_by_day,
        'orders_by_status': orders_by_status,
        'top_products': top_products,
    })