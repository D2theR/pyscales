# Import Models here
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

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
    website = models.URLField(max_length=256, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    added_by = models.CharField(max_length=64, editable=False)
    last_updated = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "%s | %s | %s | %s" % (self.name,self.customer_code,self.city,self.state_or_region)

    class Meta:
        managed = True
        unique_together = (('name', 'customer_code'),)

class CustomerContacts(models.Model):
    company = models.ForeignKey(CustomerProfile, related_name='company')
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    title = models.CharField(max_length=256,blank=True)
    position = models.CharField(max_length=256, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex],max_length=15, blank=True)
    email = models.EmailField(max_length=70, blank=True)

    def __str__(self):
        return "%s | %s %s" % (self.company, self.first_name, self.last_name)
    class Meta:
        managed = True
        unique_together = (('company', 'first_name', 'last_name'),)