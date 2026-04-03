from django.contrib import admin
from .models import GoodsCategory, GoodsInfo

@admin.register(GoodsCategory)
class GoodsCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "cag_name", "cag_css", "cag_img"]
    search_fields = ["cag_name"]

@admin.register(GoodsInfo)
class GoodsInfoAdmin(admin.ModelAdmin):
    list_display = ["id", "goods_name", "goods_price", "goods_cag"]
    list_filter = ["goods_cag"]
    search_fields = ["goods_name", "goods_desc"]