from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Comment, Product, Review
from datetime import datetime
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Sum, Avg, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def home_view(request):
    """Trang chủ: sản phẩm nổi bật + danh mục + hot deal + đánh giá khách hàng."""
    featured_products = Product.objects.filter(is_active=True).order_by('-sold_count')[:8]
    categories = Category.objects.filter(parent__isnull=True)

    # ĐÃ MỞ KHÓA TẠI ĐÂY 👇: Sửa [:4] thành [:12] để hiển thị tối đa 12 sản phẩm Flash Sale
    hot_deals = Product.objects.filter(
        is_active=True, sale_price__isnull=False
    ).order_by('-created_at')[:12]

    # Đánh giá 5 sao có nội dung, mới nhất — dùng làm "testimonial"
    testimonials = Review.objects.filter(
        rating__gte=4
    ).exclude(content='').select_related('user', 'product').order_by('-created_at')[:3]

    stats = {
        'product_count': Product.objects.filter(is_active=True).count(),
        'category_count': Category.objects.count(),
        'customer_count': Product.objects.aggregate(total=Sum('sold_count'))['total'] or 0,
    }

    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'hot_deals': hot_deals,
        'testimonials': testimonials,
        'stats': stats,
    })


def product_list_view(request):
    """
    Trang danh sách sản phẩm — gộp cả filter, search, sort trong 1 view
    thông qua query params trên URL, ví dụ:
    /products/?category=1&min_price=100000&max_price=500000&q=iphone&sort=price_asc
    """
    products = Product.objects.filter(is_active=True).select_related('category')

    # --- SEARCH ---
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # --- FILTER theo danh mục ---
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # --- FILTER theo khoảng giá ---
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # --- SORT ---
    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'best_selling': '-sold_count',
        'name_asc': 'name',
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    # --- PHÂN TRANG ---
    paginator = Paginator(products, 12)  # 12 sản phẩm / trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'sort': sort,
    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, slug):
    """Trang chi tiết sản phẩm: ảnh, giá, review, comment."""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.select_related('user').all()
    comments = product.comments.filter(parent__isnull=True).select_related('user').prefetch_related('replies')
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'reviews': reviews,
        'comments': comments,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def add_review_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content', '')

        existing = Review.objects.filter(product=product, user=request.user).first()
        if existing:
            existing.rating = rating
            existing.content = content
            existing.save()
            messages.success(request, 'Cập nhật đánh giá thành công.')
        else:
            Review.objects.create(product=product, user=request.user, rating=rating, content=content)
            messages.success(request, 'Cảm ơn bạn đã đánh giá sản phẩm!')

    return redirect('products:product_detail', slug=slug)


@login_required
def add_comment_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')

        if content:
            Comment.objects.create(
                product=product,
                user=request.user,
                content=content,
                parent_id=parent_id if parent_id else None,
            )
            messages.success(request, 'Đã đăng bình luận.')

    return redirect('products:product_detail', slug=slug)


# Từ khóa liên quan theo tháng — chỉnh sửa tùy theo mặt hàng thực tế của bạn
SEASONAL_KEYWORDS = {
    1:  ['áo khoác', 'áo len', 'tết'],
    2:  ['áo khoác', 'tết', 'du xuân'],
    3:  ['áo sơ mi'],
    4:  ['áo thun', 'quần short'],
    5:  ['áo thun', 'mùa hè'],
    6:  ['áo thun', 'quần short'],
    7:  ['áo thun', 'mùa hè'],
    8:  ['tựu trường', 'đồng phục'],
    9:  ['tựu trường', 'áo sơ mi'],
    10: ['áo khoác nhẹ'],
    11: ['áo khoác', 'sale'],
    12: ['áo khoác', 'giáng sinh'],
}


def _serialize_product(p):
    first_image = p.images.first()
    return {
        'name': p.name,
        'slug': p.slug,
        'price': float(p.current_price),
        'image': first_image.image.url if first_image else None,
        'url': reverse('products:product_detail', args=[p.slug]),
    }


def search_suggestions_view(request):
    """API JSON cho ô tìm kiếm: gợi ý theo mùa/trending (chưa gõ) hoặc live search (đang gõ)."""
    query = request.GET.get('q', '').strip()

    # ===== ĐANG GÕ — trả kết quả khớp trực tiếp =====
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query),
            is_active=True
        ).select_related('category').distinct()[:6]

        return JsonResponse({
            'mode': 'live',
            'products': [_serialize_product(p) for p in products],
        })

    # ===== CHƯA GÕ GÌ — gợi ý theo mùa + bán chạy =====
    current_month = datetime.now().month
    keywords = SEASONAL_KEYWORDS.get(current_month, [])

    seasonal_qs = Product.objects.none()
    for kw in keywords:
        seasonal_qs |= Product.objects.filter(is_active=True, name__icontains=kw)
    seasonal_products = list(seasonal_qs.select_related('category').distinct()[:4])

    # Không có sản phẩm khớp từ khóa mùa nào -> fallback sang bán chạy nhất
    if not seasonal_products:
        seasonal_products = list(
            Product.objects.filter(is_active=True).order_by('-sold_count')
            .select_related('category')[:4]
        )

    trending_products = list(
        Product.objects.filter(is_active=True)
        .exclude(id__in=[p.id for p in seasonal_products])
        .order_by('-sold_count').select_related('category')[:4]
    )

    trending_keywords = list(Category.objects.all().values_list('name', flat=True)[:8])

    return JsonResponse({
        'mode': 'suggest',
        'trending_keywords': trending_keywords,
        'seasonal_products': [_serialize_product(p) for p in seasonal_products],
        'trending_products': [_serialize_product(p) for p in trending_products],
    })