from django.db import models
from django.contrib.auth.models import UserManager,PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone



class User(AbstractBaseUser,PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=200, validators=[username_validator],error_messages={'unique': _("A user with that username already exists."),},)
    full_name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(unique=True,blank=False,null=False)
    location = models.CharField(max_length=100,null=True,blank=True)
    phone_number = models.CharField(max_length=100,null=True,blank=True)
    bio = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    image = models.ImageField(default='profile_pics/demo.png', upload_to='profile_pics')
    is_staff = models.BooleanField(_('staff status'),default=False,)
    is_active = models.BooleanField(_('active'),default=True,)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('alluser')
        verbose_name_plural = _('allusers')
        


class ProfileType(models.Model):
    title = models.CharField(max_length=100,null=False,blank=False)

    class Meta:
        db_table = 'profile_types'

    def __str__(self):
        return self.title



class Plan(models.Model):
    title = models.CharField(max_length=100,null=False,blank=False)
    amount = models.FloatField(default=0)
    goal_amount = models.FloatField(default=0)
    blog_amount = models.FloatField(default=0)
    extra_goal_cost = models.FloatField(default=0)


class Country(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'countries'

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.PROTECT)
    profile_type = models.ForeignKey(ProfileType, on_delete=models.PROTECT)
    ngo_profile_id = models.CharField(max_length=100, null=True, blank=True)
    profile_name = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100,null=True,blank=True)
    bio = models.TextField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT, db_column='country')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    image = models.ImageField(default='profile_pics/demo.png', upload_to='ngo_and_donee_profile_pics')
    rut_path = models.FileField(null=True,blank=True)
    cdc_path= models.FileField(null=True,blank=True)
    id_front= models.FileField(null=True,blank=True)
    id_back= models.FileField(null=True,blank=True)
    is_approved= models.BooleanField(default=False)
    view_count= models.PositiveIntegerField(default=0)
    plan_id= models.ForeignKey(Plan, on_delete=models.PROTECT, null=True, blank=True)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return self.profile_name
