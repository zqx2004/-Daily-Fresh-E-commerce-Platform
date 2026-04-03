from django.contrib import admin
from .models import OrderInfo, OrderGoods

class OrderGoodsInline(admin.TabularInline):
    model = OrderGoods
    extra = 0

@admin.register(OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ["id", "order_sn", "receiver", "phone", "status"]
    search_fields = ["order_sn", "receiver", "phone"]
    inlines = [OrderGoodsInline]

# 只注册一次，避免重复注册错误
# @admin.register(OrderGoods)
class OrderGoodsAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "goods", "quantity"]
    search_fields = ["goods__goods_name", "order__order_sn"]