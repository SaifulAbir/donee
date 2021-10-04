from django.db import models

from Donee.models import DoneeModel
from user.models import Profile


class Goal(models.Model):
    CHOICES = [
    ('Draft', 'Draft'),
    ('Publish', 'Publish'),]

    title = models.CharField(max_length=500)
    short_description = models.CharField(max_length=800)
    full_description = models.CharField(max_length=2000)
    buying_item = models.CharField(max_length=200)
    online_source_url =models.URLField(max_length=400)
    unit_cost = models.FloatField()
    total_unit = models.IntegerField(default=1)
    pgw_amount = models.FloatField()
    ngo_amount = models.FloatField()
    platform_amount = models.FloatField()
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, default=CHOICES[0][0])
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_id = models.ForeignKey(Profile,on_delete=models.CASCADE)


class Media(models.Model):
    CHOICES = [
    ('In_Queue', 'In_Queue'),
    ('In_Processing', 'In_Processing'),
    ('Complete','Complete'),]

    goal = models.ForeignKey(Goal, on_delete=models.CASCADE)	
    type = models.IntegerField(default=0)
    name  = models.CharField(max_length=400)
    file = models.FileField(upload_to='goals') 
    status = models.CharField(max_length=20, default=CHOICES[0][0])


class SDGS(DoneeModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'SDGS'
        verbose_name_plural = 'SDGS'
        db_table = 'sdgs'

    def __str__(self):
        return self.name