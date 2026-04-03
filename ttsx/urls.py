"""
URL configuration for ttsx project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 主路由：解耦应用路由，便于维护
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("goods.urls")),  # 商品模块路由
    path("cart/", include("cart.urls")),  # 购物车/订单模块路由
]

# 开发环境提供静态文件 + 媒体文件访问（必须加上！）
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)