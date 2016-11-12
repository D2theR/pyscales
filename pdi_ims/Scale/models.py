from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# Create your models here...

class ScaleManager(models.Model):
    scale_number = models.IntegerField(blank=False)
    scale_name = models.CharField(max_length=64, blank=False)
    date_last_serviced = models.DateTimeField(blank=True,null=True)
    added_by = models.CharField(max_length=64, blank=True, editable=False)
    last_updated = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return "%i | %s" % (self.scale_number, self.scale_name)

    class Meta:
        managed = True
        unique_together = (('scale_name','scale_number'),)

class ScaleVerification(models.Model):
    scale_verified = models.ForeignKey(ScaleManager, related_name='scale_verified')
    weight = models.DecimalField(max_digits=64, decimal_places=2)
    user_name = models.CharField(max_length=64, blank=True, editable=False)
    date_recorded = models.DateTimeField(auto_now_add=True, editable=False)
    tolerance = models.DecimalField(max_digits=8, decimal_places=3, blank=True, null=True)
    check_weight = models.DecimalField(max_digits=64, decimal_places=3, blank=True, null=True)
    verified = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
    def __str__(self):
        return "%s, %f, %s, %f, %f, %s, %s" %(self.scale_verified, self.weight, self.user_name, self.tolerance, self.check_weight, self.verified, self.date_recorded)