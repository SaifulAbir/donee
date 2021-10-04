from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from Donee.models import DoneeModel


class Country(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'countries'

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser,PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=200, validators=[username_validator],error_messages={'unique': _("A user with that username already exists."),},)
    full_name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(unique=True,blank=False,null=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True, db_column='country')
    phone_number = models.CharField(max_length=100,null=True,blank=True)
    bio = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    image = models.ImageField(default='images/demo.png', upload_to='images/user_profile_pictures')
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


class Plan(models.Model):
    title = models.CharField(max_length=100,null=False,blank=False)
    amount = models.FloatField(default=0)
    goal_amount = models.FloatField(default=0)
    blog_amount = models.FloatField(default=0)
    extra_goal_cost = models.FloatField(default=0)


class Profile(models.Model):
    PROFILE_TYPES = (
        ('NGO', 'NGO'),
        ('DONEE', 'DONEE'),
    )

    user = models.OneToOneField(User,on_delete=models.PROTECT)
    profile_type = models.CharField(max_length=20, blank=False, null=False,
                                     choices=PROFILE_TYPES)
    ngo_profile_id = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100,null=True,blank=True)
    bio = models.TextField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True, db_column='country')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    image = models.ImageField(default='images/demo.png', upload_to='images/ngo_and_donee_profile_pictures')
    rut_path = models.FileField(null=True,blank=True, upload_to='images')
    cdc_path= models.FileField(null=True,blank=True, upload_to='images')
    id_front= models.FileField(null=True,blank=True, upload_to='images')
    id_back= models.FileField(null=True,blank=True, upload_to='images')
    is_approved= models.BooleanField(default=False)
    view_count= models.PositiveIntegerField(default=0)
    plan_id= models.ForeignKey(Plan, on_delete=models.PROTECT, null=True, blank=True)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return self.username


class Notification(DoneeModel):
    donee_notification = models.BooleanField(default=False)
    account_activity = models.BooleanField(default=False)
    donee_activity = models.BooleanField(default=False)
    achieved_goals = models.BooleanField(default=False)
    new_followers = models.BooleanField(default=False)
    NGO_role_assign = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, db_column='user', related_name='user_notification')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True, db_column='profile', related_name='profile_notification')

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        db_table = 'notifications'

    def __str__(self):
        return self.user
