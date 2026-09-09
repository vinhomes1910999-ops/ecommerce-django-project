from .models import Cart


def cart_summary(request):
    """Trả về số lượng sản phẩm trong giỏ, dùng ở navbar mọi trang."""
    cart_items_count = 0
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items_count = cart.total_items
    return {'cart_items_count': cart_items_count}