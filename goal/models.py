from django.db import models
from Donee.models import DoneeModel
from django.db.models.signals import pre_save
from .utils import unique_slug_generator
from user.models import Profile,User




class Setting(DoneeModel):
    pgw = models.IntegerField(default=0)
    ngo = models.IntegerField(default=0)
    platform = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Setting'
        verbose_name_plural = 'Settings'
        db_table = 'settings'






class Goal(DoneeModel):
    
    GOAL_STATUSES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
        ('COMPLETED', 'Completed'),]

    title = models.CharField(max_length=500)
    slug = models.SlugField(null=False, blank=False, allow_unicode=True)
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
    pgw_percentage = models.IntegerField(default=0)
    ngo_percentage = models.IntegerField(default=0)
    platform_percentage = models.IntegerField(default=0)
    total_amount = models.DecimalField(max_digits=19, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=GOAL_STATUSES, default=GOAL_STATUSES[0][0])
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="profile_goal")
    total_like_count = models.IntegerField(default=0)
    total_comment_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Goal'
        verbose_name_plural = 'Goals'
        db_table = 'goals'

    def __str__(self):
        return self.title

    def save(self,*args, **kwargs):
        super(Goal,self).save(*args, **kwargs)
        a = Setting.objects.first()
        if self.pgw_percentage == 0:
            self.pgw_percentage = a.pgw
            self.ngo_percentage = a.ngo
            self.platform_percentage = a.platform
            self.save()
       
       

def pre_save_receiver_goal(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

pre_save.connect(pre_save_receiver_goal, sender=Goal)




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




class Like(DoneeModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name='goal_user')
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name = 'goal_like')
    is_like = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name ='profile_like',null=True,blank=True)


    class Meta:
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
        db_table = 'like'

    def __str__(self):
        return self.goal.title


class Comment(DoneeModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name='comment_user')
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name = 'goal_comment')
    text = models.TextField()
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name ='profile_comment',null=True,blank=True)


    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        db_table = 'comment'

    def __str__(self):
        return self.goal.title


class GoalSave(DoneeModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name='goalsave_user')
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT, related_name = 'saved_goal')
    is_saved = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name ='profile_goalsave',null=True,blank=True)


    class Meta:
        verbose_name = 'GoalSave'
        verbose_name_plural = 'GoalSaves'
        db_table = 'goalsave'

    def __str__(self):
        return self.goal.title


