from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from products.models import Product
from .models import Cart, CartItem


@login_required
def cart_detail_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@login_required
def add_to_cart_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    # --- BẮT LẤY THÔNG TIN MÀU VÀ SIZE TỪ FORM HTML ---
    color = request.POST.get('color', '')
    size = request.POST.get('size', '')

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:
        messages.error(request, f'Chỉ còn {product.stock} sản phẩm trong kho.')
        return redirect('products:product_detail', slug=product.slug)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    # --- ĐƯA MÀU VÀ SIZE VÀO ĐỂ PHÂN BIỆT SẢN PHẨM TRONG GIỎ ---
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        color=color, # Thêm dòng này
        size=size,   # Thêm dòng này
        defaults={'quantity': quantity}
    )

    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, f'Không thể thêm — vượt quá tồn kho ({product.stock}).')
            return redirect('products:product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()

    # Làm cho câu thông báo xịn xò hơn
    variant_info = []
    if color: variant_info.append(color)
    if size: variant_info.append(size)
    
    if variant_info:
        msg = f'Đã thêm "{product.name}" ({", ".join(variant_info)}) vào giỏ hàng.'
    else:
        msg = f'Đã thêm "{product.name}" vào giỏ hàng.'

    messages.success(request, msg)
    return redirect('cart:cart_detail')


@login_required
def update_cart_item_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
        elif quantity > cart_item.product.stock:
            messages.error(request, f'Chỉ còn {cart_item.product.stock} sản phẩm trong kho.')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Đã cập nhật số lượng.')

    return redirect('cart:cart_detail')


@login_required
def remove_from_cart_view(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Đã xóa sản phẩm khỏi giỏ hàng.')
    return redirect('cart:cart_detail')