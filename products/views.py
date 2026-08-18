from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Comment, Product, Review


def home_view(request):
    """Trang chủ: hiển thị sản phẩm nổi bật + danh mục."""
    featured_products = Product.objects.filter(is_active=True).order_by('-sold_count')[:8]
    categories = Category.objects.filter(parent__isnull=True)  # chỉ lấy danh mục cha
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'categories': categories,
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

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


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