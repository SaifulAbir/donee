from django.db import models


class DoneeModel(models.Model):
    created_by = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(max_length=255, null=True)
    modified_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True