from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from Inventory import models as items

# Create your models here.
class CustomerProfile(models.Model):
    name = models.CharField(max_length=128)
    customer_code = models.CharField(max_length=128)
    address_line_1 = models.CharField(max_length=256)
    address_line_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256)
    state_or_region = models.CharField(max_length=256)
    zip_or_region_code = models.CharField(max_length=256)
    country = models.CharField(max_length=256)
    comments = models.TextField(blank=True, null=True)
    added_by = models.CharField(max_length=64, editable=False)
    last_updated = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "%s | %s | %s | %s" % (self.name,self.customer_code,self.city,self.state_or_region)

    class Meta:
        managed = True
        unique_together = (('name', 'customer_code'),)

class SupplierProfile(models.Model):
    name = models.CharField(max_length=128)
    supplier_code = models.CharField(max_length=128)
    address_line_1 = models.CharField(max_length=256)
    address_line_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256)
    state_or_region = models.CharField(max_length=256)
    zip_or_region_code = models.CharField(max_length=256)
    country = models.CharField(max_length=256)
    comments = models.TextField(blank=True, null=True)
    added_by = models.CharField(max_length=64, editable=False)
    last_updated = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "%s | %s | %s | %s" % (self.name,self.supplier_code,self.city,self.state_or_region)

    class Meta:
        managed = True
        unique_together = (('name', 'supplier_code'),)

class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length=96)
    supplier = models.ForeignKey(SupplierProfile, related_name='supplier')
    iuc_to_order = models.ManyToManyField(items.InventoryItem, through='PO_Item')
    date_ordered = models.DateTimeField(auto_now_add=True, editable=False)
    placed_by = models.CharField(max_length=64, editable=False)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):              # __unicode__ on Python 2
        return "%s | %s" % (self.po_number, self.date_ordered)

    class Meta:
        unique_together = (('id','po_number'),)
        managed = True

class PO_Item(models.Model):
    order_number = models.ForeignKey(PurchaseOrder, related_name='order_number')
    item_ordered = models.ForeignKey(items.InventoryItem, related_name="item_ordered", limit_choices_to={'category':'RAW'})
    lot_number = models.CharField(max_length=128, blank=True, null=True)
    lbs_ordered = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    lbs_received = models.DecimalField(max_digits=64, decimal_places=2, blank=True, null=True)
    date_received = models.DateTimeField()
    lab_approval = models.BooleanField(default=False)
    barcode_data = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "%s | %s | %s" % (self.order_number, self.item_ordered, self.lot_number)

    class Meta:
        unique_together = (('id','order_number','item_ordered'),)
        managed = True
