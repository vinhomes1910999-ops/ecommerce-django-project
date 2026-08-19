from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Promotion, Review, Comment
from django.contrib.humanize.templatetags.humanize import intcomma


# ===================== INLINE: Ảnh sản phẩm =====================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'preview', 'is_thumbnail', 'sort_order')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px; border-radius:6px; object-fit:cover;" />',
                obj.image.url
            )
        return "—"
    preview.short_description = "Xem trước"


# ===================== INLINE: Review (chỉ xem, không sửa) =====================
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ('user', 'rating', 'content', 'created_at')
    readonly_fields = ('user', 'rating', 'content', 'created_at')
    can_delete = True

    def has_add_permission(self, request, obj=None):
        # Review phải do khách hàng tạo qua site, admin chỉ xem/xóa, không tự thêm
        return False


# ===================== CATEGORY =====================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'product_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('parent',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Số sản phẩm"


# ===================== PRODUCT (trọng tâm) =====================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    # ---------- LIST VIEW ----------
    list_display = (
        'thumbnail', 'name', 'category', 'price_display',
        'stock_badge', 'sold_count', 'is_active', 'created_at',
    )
    list_display_links = ('thumbnail', 'name')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'slug')
    list_per_page = 25
    list_editable = ('is_active',)          # sửa nhanh trạng thái ngay trên bảng list
    ordering = ('-created_at',)

    # ---------- FORM (ADD/CHANGE VIEW) ----------
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('category',)      # dropdown tìm kiếm thay vì <select> dài
    inlines = [ProductImageInline, ReviewInline]

    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('name', 'slug', 'category', 'description'),
        }),
        ('Giá & Tồn kho', {
            'fields': (('price', 'sale_price'), ('stock', 'sold_count')),
            'description': 'Để trống "Giá khuyến mại" nếu sản phẩm không giảm giá.',
        }),
        ('Trạng thái', {
            'fields': ('is_active',),
            'classes': ('collapse',),        # gập lại mặc định, đỡ rối mắt
        }),
    )

    # ---------- CUSTOM COLUMNS ----------
    def thumbnail(self, obj):
        first_image = obj.images.first()
        if first_image:
            return format_html(
                '<img src="{}" style="height:45px; width:45px; object-fit:cover; border-radius:6px;" />',
                first_image.image.url
            )
        return format_html('<span style="color:#ccc;">Chưa có ảnh</span>')
    thumbnail.short_description = "Ảnh"

    def price_display(self, obj):
        if obj.sale_price:
            return format_html(
                '<span style="text-decoration:line-through; color:#999; font-size:12px;">{} đ</span><br>'
                '<span style="color:#dc3545; font-weight:bold;">{} đ</span>',
                intcomma(obj.price), intcomma(obj.sale_price)
            )
        return format_html('<span style="font-weight:bold;">{} đ</span>', intcomma(obj.price))
    price_display.short_description = "Giá bán"

    def stock_badge(self, obj):
        if obj.stock == 0:
            color, text = '#dc3545', 'Hết hàng'
        elif obj.stock < 10:
            color, text = '#fd7e14', f'{obj.stock} (Sắp hết)'
        else:
            color, text = '#198754', str(obj.stock)
        return format_html(
            '<span style="background:{}; color:white; padding:3px 10px; border-radius:12px; font-size:12px;">{}</span>',
            color, text
        )
    stock_badge.short_description = "Tồn kho"


# ===================== PROMOTION / REVIEW / COMMENT (bổ sung nhanh) =====================
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('product', 'discount_type', 'discount_value', 'start_date', 'end_date', 'is_active')
    list_filter = ('discount_type', 'is_active')
    autocomplete_fields = ('product',)
    search_fields = ('product__name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    autocomplete_fields = ('product', 'user')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'parent', 'created_at')
    search_fields = ('product__name', 'user__username', 'content')
    autocomplete_fields = ('product', 'user', 'parent')