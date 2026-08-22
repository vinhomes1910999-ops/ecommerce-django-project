from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Giỏ hàng của {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # ===== THÊM 2 CỘT NÀY ĐỂ LƯU MÀU VÀ SIZE =====
    color = models.CharField("Màu sắc", max_length=50, blank=True, null=True)
    size = models.CharField("Kích thước", max_length=50, blank=True, null=True)
    
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # QUAN TRỌNG: Cập nhật bộ lọc để phân biệt được "Áo đỏ size L" và "Áo đen size M"
        unique_together = ('cart', 'product', 'color', 'size')

    @property
    def subtotal(self):
        return self.product.current_price * self.quantity

    def __str__(self):
        # Nâng cấp hiển thị tên trong Admin cho dễ nhìn
        variant = []
        if self.color: variant.append(self.color)
        if self.size: variant.append(self.size)
        variant_str = f" ({', '.join(variant)})" if variant else ""
        return f"{self.quantity} x {self.product.name}{variant_str}"