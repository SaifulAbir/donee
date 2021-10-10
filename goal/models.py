from django.db import models
from Donee.models import DoneeModel


class Goal(DoneeModel):
    from user.models import Profile
    GOAL_STATUSES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),]

    title = models.CharField(max_length=500)
    short_description = models.CharField(max_length=800)
    full_description = models.TextField()
    buying_item = models.CharField(max_length=200)
    online_source_url =models.URLField(max_length=400)
    image = models.ImageField(upload_to='images/goal_images')
    unit_cost = models.DecimalField(max_digits=19, decimal_places=2)
    total_unit = models.IntegerField(default=1)
    pgw_amount = models.DecimalField(max_digits=19, decimal_places=2)
    ngo_amount = models.DecimalField(max_digits=19, decimal_places=2)
    platform_amount = models.DecimalField(max_digits=19, decimal_places=2)
    total_amount = models.DecimalField(max_digits=19, decimal_places=2)
    status = models.CharField(max_length=20, choices=GOAL_STATUSES, default=GOAL_STATUSES[0][0])
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        db_table = 'goals'

    def __str__(self):
        return self.title


class Media(DoneeModel):
    CHOICES = [
        ('IN_QUEUE', 'In_Queue'),
        ('IN_PROCESSING', 'In_Processing'),
        ('COMPLETE', 'Complete'),]

    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    VIDEO_TYPES = [
        ('UPDATE', 'Update'),
        ('THANK_YOU', 'Thank you'),
    ]

    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name='goal_media')
    type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='goals')
    status = models.CharField(max_length=20, choices=CHOICES)
    video_type = models.CharField(max_length=50, null=True, blank=True, choices=VIDEO_TYPES)

    class Meta:
        verbose_name = 'Media'
        verbose_name_plural = 'Media'
        db_table = 'media'


class SDGS(DoneeModel):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    thumbnail = models.ImageField(upload_to='images/sdgs_thumbnail', blank=True, null=True)
    status = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'SDGS'
        verbose_name_plural = 'SDGS'
        db_table = 'sdgs'

    def __str__(self):
        return self.title


class GoalSDGS(DoneeModel):
    """
        sdgs: one to many relation
    """
    sdgs = models.ForeignKey(
        SDGS, related_name='sdgs_goal', on_delete=models.PROTECT,
        verbose_name='SDGS'
    )
    goal = models.ForeignKey(
        Goal, related_name='goal_sdgs', on_delete=models.PROTECT,
        verbose_name='Goal'
    )

    class Meta:
        verbose_name = 'GoalSDGS'
        verbose_name_plural = 'GoalSDGS'
        db_table = 'goal_sdgs'


class Setting(DoneeModel):
    pgw = models.IntegerField(default=0)
    ngo = models.IntegerField(default=0)
    platform = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        db_table = 'settings'