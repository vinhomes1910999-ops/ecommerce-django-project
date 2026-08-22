from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Chờ xác nhận'
        CONFIRMED = 'confirmed', 'Đã xác nhận'
        SHIPPING = 'shipping', 'Đang giao'
        COMPLETED = 'completed', 'Hoàn thành'
        CANCELLED = 'cancelled', 'Đã hủy'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    order_code = models.CharField(max_length=30, unique=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    shipping_address = models.CharField(max_length=255)
    shipping_phone = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_code


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)   # snapshot
    price = models.DecimalField(max_digits=12, decimal_places=2)  # snapshot
    quantity = models.PositiveIntegerField()

    # ===== THÊM 2 CỘT MÀU VÀ SIZE (snapshot) =====
    color = models.CharField("Màu sắc", max_length=50, blank=True, null=True)
    size = models.CharField("Kích thước", max_length=50, blank=True, null=True)
    # =============================================

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        # Hiển thị luôn màu/size ra Admin cho dễ gói hàng
        variant = []
        if self.color: variant.append(self.color)
        if self.size: variant.append(self.size)
        variant_str = f" ({', '.join(variant)})" if variant else ""
        return f"{self.quantity} x {self.product_name}{variant_str}"


class Payment(models.Model):
    class Method(models.TextChoices):
        COD = 'cod', 'Thanh toán khi nhận hàng'
        BANK_TRANSFER = 'bank_transfer', 'Chuyển khoản'
        VNPAY = 'vnpay', 'VNPay'
        MOMO = 'momo', 'Momo'

    class Status(models.TextChoices):
        UNPAID = 'unpaid', 'Chưa thanh toán'
        PAID = 'paid', 'Đã thanh toán'
        FAILED = 'failed', 'Thất bại'
        REFUNDED = 'refunded', 'Đã hoàn tiền'

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.COD)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)
    paid_at = models.DateTimeField(null=True, blank=True)
    transaction_ref = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Thanh toán cho {self.order.order_code}"