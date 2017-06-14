from django.db import models
from django.utils.html import format_html, format_html_join, mark_safe
from decimal import Decimal
from django.contrib.auth.models import User
from suppliers import models as supply

# Create your models here.
class IngredientList(models.Model):
    item_code = models.CharField(max_length=64, blank=False, null=False)
    category = models.CharField(max_length=256, blank=False, null=False,choices=[('RAW','Raw Material'),('FG','Finished Good'),('PKG','Packaging'),('LBL','Labeling')])
    name = models.CharField(max_length=64, blank=False, null=False)
    chemical_name = models.CharField(max_length=256, blank=False, null=True)
    synonyms = models.CharField(max_length=300, blank=True)
    customer_supplied = models.BooleanField(default=False)
    supplier = models.ForeignKey(supply.SupplierProfile, related_name='supplier')
    manufacturer = models.CharField(max_length=96, blank=True)
    specific_gravity = models.DecimalField(max_digits=8, decimal_places=4)
    origin_country = models.CharField(max_length=128, blank=True)
    nafta_tariff = models.CharField(max_length=64, blank=True)
    nafta_last_updated = models.DateField()
    cas_number = models.CharField(max_length=64, blank=True)
    approved_by = models.CharField(max_length=64, editable=False)
    date_approved = models.DateTimeField(auto_now_add=True, editable=False)
    comments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return "%s | %s | %s" % (self.item_code,self.name,self.supplier)

    def _get_pubchem_url(self):
        return format_html('<a href="https://www.ncbi.nlm.nih.gov/pccompound?term={}">Search PubChem</a>', mark_safe(self.chemical_name.replace(' ','+')))
        #return "%s" % (self.chemical_name)
    
    def _get_chemid_url(self):
        return format_html('<a href="https://chem.nlm.nih.gov/chemidplus/name/{}">Search ChemIDplus</a>', mark_safe(self.chemical_name.replace(' ','+')))

    ###Readonly calculated class fields
    pubchem_search = property(_get_pubchem_url)
    chemID_search = property(_get_chemid_url)
    class Meta:
        managed = True
        unique_together = (('item_code', 'category', 'name', 'supplier'),)

class ItemPricing(models.Model):
    item = models.ForeignKey(IngredientList, related_name='item')
    packaging_type = models.CharField(max_length=256, blank=False, null=False,choices=[('BOX','Boxes'),('BAG','Bags'),('SKD', 'Skids'),('DRM','Drums'),('PLS','Pails'),('SS','Super-sack'), ('OTH','Other')])
    unit_type = models.CharField(max_length=256, blank=True, null=True, choices=[('LBS','LBS'),('KGS','KGS')])
    min_qty = models.DecimalField(max_digits=16, decimal_places=3, blank=True, null=True, default=Decimal(0.000))
    max_qty = models.DecimalField(max_digits=16, decimal_places=3, blank=True, null=True, default=Decimal(0.000))
    price = models.DecimalField(verbose_name="Price($)" ,max_digits=16, decimal_places=2, blank=True, null=True, default=Decimal(0.00))
    best_price = models.BooleanField(default=False)
    lead_time = models.DecimalField(verbose_name="Lead Time(Days)",max_digits=12, decimal_places=1, blank=True, null=True, default=Decimal(0.00))
    fob_point = models.CharField(max_length=256, blank=True, null=True)
    freight_type = models.CharField(max_length=256, blank=False, null=True, choices=[('CPU','CPU'),('DEL','Delivered'),('OTHER','Other')])
    freight_cost = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True, default=Decimal(0.000))
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, editable=False)
    

    def __str__(self):
        return "%s" % (self.item)

    class Meta:
        managed = True
        verbose_name = "Item Pricing"
        unique_together = ('id','item')