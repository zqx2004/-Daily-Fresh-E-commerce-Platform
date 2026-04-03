from django.db import models
from goods.models import GoodsInfo

class OrderInfo(models.Model):
    order_sn = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    receiver = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    freight = models.IntegerField(default=1000)
    remark = models.CharField(max_length=200, blank=True)
    status = models.IntegerField(default=1)

    class Meta:
        db_table = 'cart_orderinfo'

class OrderGoods(models.Model):
    goods = models.ForeignKey(GoodsInfo, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE)

    class Meta:
        db_table = 'cart_ordergoods'