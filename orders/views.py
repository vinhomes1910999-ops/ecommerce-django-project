from django.shortcuts import render
import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Cart
from .models import Order, OrderItem, Payment


@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if not cart.items.exists():
        messages.error(request, 'Giỏ hàng của bạn đang trống.')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '').strip()
        shipping_phone = request.POST.get('shipping_phone', '').strip()
        payment_method = request.POST.get('payment_method', 'cod')
        note = request.POST.get('note', '')

        if not shipping_address or not shipping_phone:
            messages.error(request, 'Vui lòng nhập đầy đủ địa chỉ và số điện thoại.')
            return render(request, 'orders/checkout.html', {'cart': cart})

        # --- Kiểm tra tồn kho lần cuối trước khi tạo đơn (tránh race condition) ---
        for item in cart.items.select_related('product').all():
            if item.quantity > item.product.stock:
                messages.error(request, f'"{item.product.name}" chỉ còn {item.product.stock} sản phẩm.')
                return redirect('cart:cart_detail')

        # --- Tạo đơn hàng trong 1 transaction — đảm bảo toàn vẹn dữ liệu ---
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                order_code=f"ORD{uuid.uuid4().hex[:10].upper()}",
                shipping_address=shipping_address,
                shipping_phone=shipping_phone,
                note=note,
                total_amount=cart.total_price,
            )

            for item in cart.items.select_related('product').all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    price=item.product.current_price,
                    quantity=item.quantity,
                    # ===== CHÉP MÀU SẮC VÀ KÍCH THƯỚC TỪ GIỎ HÀNG SANG HÓA ĐƠN =====
                    color=item.color,
                    size=item.size,
                    # =============================================================
                )
                # Trừ tồn kho + cộng số lượng đã bán
                item.product.stock -= item.quantity
                item.product.sold_count += item.quantity
                item.product.save()

            Payment.objects.create(order=order, method=payment_method)

            # Xóa sạch giỏ hàng sau khi đặt thành công
            cart.items.all().delete()

        messages.success(request, f'Đặt hàng thành công! Mã đơn: {order.order_code}')
        return redirect('orders:order_success', order_code=order.order_code)

    return render(request, 'orders/checkout.html', {'cart': cart})


@login_required
def order_success_view(request, order_code):
    order = get_object_or_404(Order, order_code=order_code, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_code):
    order = get_object_or_404(Order, order_code=order_code, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})