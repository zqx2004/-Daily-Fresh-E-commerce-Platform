from django.db import models

class GoodsCategory(models.Model):
    cag_name = models.CharField(max_length=30)
    cag_css = models.CharField(max_length=20)
    cag_img = models.ImageField(upload_to='category')

    class Meta:
        db_table = 'goods_goodscategory'

class GoodsInfo(models.Model):
    goods_name = models.CharField(max_length=100)
    goods_price = models.IntegerField(default=0)
    goods_desc = models.CharField(max_length=1000)
    goods_img = models.ImageField(upload_to='goods')
    goods_cag = models.ForeignKey(GoodsCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = 'goods_goodsinfo'