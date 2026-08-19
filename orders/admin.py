from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import intcomma
from .models import Order, OrderItem, Payment


# ===================== INLINE: Chi tiết đơn hàng =====================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'product_name', 'price', 'quantity', 'subtotal_display')
    readonly_fields = ('product_name', 'price', 'subtotal_display')  # snapshot — không cho sửa
    autocomplete_fields = ('product',)

    def subtotal_display(self, obj):
        return f"{intcomma(obj.subtotal)} đ" if obj.pk else "—"
    subtotal_display.short_description = "Thành tiền"

    def has_add_permission(self, request, obj=None):
        # Đơn hàng đã snapshot lúc checkout — admin không tự thêm item mới từ đây
        return False


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    fields = ('method', 'status', 'paid_at', 'transaction_ref')


# ===================== ORDER (trọng tâm) =====================
STATUS_COLORS = {
    'pending':   '#6c757d',   # xám
    'confirmed': '#0d6efd',   # xanh dương
    'shipping':  '#fd7e14',   # cam
    'completed': '#198754',   # xanh lá
    'cancelled': '#dc3545',   # đỏ
}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    # ---------- LIST VIEW ----------
    list_display = (
        'order_code', 'user', 'status_badge', 'total_display',
        'shipping_phone', 'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('order_code', 'user__username', 'user__email', 'shipping_phone')
    date_hierarchy = 'created_at'          # thanh điều hướng Năm > Tháng > Ngày
    list_per_page = 25
    ordering = ('-created_at',)
    autocomplete_fields = ('user',)

    # ---------- FORM ----------
    inlines = [OrderItemInline, PaymentInline]
    readonly_fields = ('order_code', 'total_amount', 'created_at', 'updated_at')

    fieldsets = (
        ('Thông tin đơn hàng', {
            'fields': ('order_code', 'user', 'status'),
        }),
        ('Giao hàng', {
            'fields': ('shipping_address', 'shipping_phone', 'note'),
        }),
        ('Tổng kết', {
            'fields': ('total_amount',),
        }),
        ('Nhật ký hệ thống', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    # ---------- CUSTOM ACTIONS ----------
    actions = ['mark_as_completed', 'mark_as_shipping']

    @admin.action(description="✅ Đánh dấu các đơn đã chọn là Hoàn thành")
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"Đã cập nhật {updated} đơn hàng sang trạng thái Hoàn thành.")

    @admin.action(description="🚚 Đánh dấu các đơn đã chọn là Đang giao")
    def mark_as_shipping(self, request, queryset):
        updated = queryset.update(status='shipping')
        self.message_user(request, f"Đã cập nhật {updated} đơn hàng sang trạng thái Đang giao.")

    # ---------- CUSTOM COLUMNS ----------
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{}; color:white; padding:4px 12px; '
            'border-radius:12px; font-size:12px; font-weight:500;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Trạng thái"

    def total_display(self, obj):
        return format_html('<b>{} đ</b>', intcomma(obj.total_amount))
    total_display.short_description = "Tổng tiền"