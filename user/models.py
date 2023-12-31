from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from Donee.models import DoneeModel
import random
import string


class Country(models.Model):
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=25)

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

phone_regex = RegexValidator(regex='^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\./0-9]*$',message='invalid phone number')
class User(AbstractBaseUser,PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(max_length=200, validators=[username_validator],error_messages={'unique': _("A user with that username already exists."),},)
    full_name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(unique=True,blank=False,null=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True, db_column='country')
    phone_number = models.CharField(max_length=255, validators=[phone_regex],null=True)
    bio = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,null=True,blank=True)
    social_status = models.CharField(max_length=20,null=True, blank=True)
    image = models.ImageField(default='images/demo.png', upload_to='images/user_profile_pictures')
    is_staff = models.BooleanField(_('staff status'),default=False,)
    is_active = models.BooleanField(_('active'),default=True,)
    total_donated_amount = models.DecimalField(max_digits=19, decimal_places=2, default=0)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    modified_at = models.DateTimeField(null=True)
    is_modified = models.BooleanField(default=False)
    total_follow_count = models.IntegerField(default=0)
    total_following_count = models.IntegerField(default=0)
    verification_id = models.CharField(default='null',max_length=40)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    #REQUIRED_FIELDS = ['email']

    def verification_id_generator(self,size=8, chars=string.ascii_uppercase + string.digits):
        result_str = ''.join(random.choice(chars) for i in range(size))
        return result_str


    def save(self, *args, **kwargs):
        super(User,self).save(*args, **kwargs)
        if self.is_active == False and self.verification_id == 'null':
            veri_id = self.verification_id_generator()
            self.verification_id = veri_id
            self.save()
    

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

    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='user_profile')
    profile_type = models.CharField(max_length=20, blank=False, null=False,
                                     choices=PROFILE_TYPES)
    ngo_profile_id = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100,null=True,blank=True)
    bio = models.TextField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=True, blank=True, db_column='country')
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=255, validators=[phone_regex], null=True)
    image = models.ImageField(default='images/demo.png', upload_to='images/ngo_and_donee_profile_pictures')
    invitation_id = models.CharField(default='null',max_length=40)
    rut_path = models.FileField(null=True,blank=True, upload_to='images')
    cdc_path= models.FileField(null=True,blank=True, upload_to='images')
    id_front= models.FileField(null=True,blank=True, upload_to='images')
    id_back= models.FileField(null=True,blank=True, upload_to='images')
    is_approved= models.BooleanField(default=False)
    view_count= models.PositiveIntegerField(default=0)
    plan_id= models.ForeignKey(Plan, on_delete=models.PROTECT, null=True, blank=True)
    total_follow_count = models.IntegerField(default=0)
    is_active= models.BooleanField(default=True)
    created_at= models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return self.username
    
    def invitation_id_generator(self,size=8, chars=string.ascii_uppercase + string.digits):
        result_str = ''.join(random.choice(chars) for i in range(size))
        return result_str
    

    def save(self, *args, **kwargs):
        super(Profile,self).save(*args, **kwargs)
        if self.profile_type == 'NGO' and self.invitation_id == 'null':
            inv_id = self.invitation_id_generator()
            self.invitation_id = inv_id
            self.save()
        
           
    

class CertificationIncorporation(DoneeModel):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, null=True, db_column='profile', related_name='profile_certification')
    file = models.FileField(upload_to='certification_of_incorporation')

    class Meta:
        verbose_name = 'Certification of incorporation'
        verbose_name_plural = 'Certification of incorporation'
        db_table = 'Certification_of_incorporation'

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


class ProfileSDGS(DoneeModel):
    """
        sdgs: one to many relation
    """
    from goal.models import SDGS
    sdgs = models.ForeignKey(
        SDGS, related_name='sdgs_profile', on_delete=models.PROTECT,
        verbose_name='SDGS'
    )
    profile = models.ForeignKey(
        Profile, related_name='profile_sdgs', on_delete=models.PROTECT,
        verbose_name='Profile'
    )

    class Meta:
        verbose_name = 'ProfileSDGS'
        verbose_name_plural = 'ProfileSDGS'
        db_table = 'profile_sdgs'


class UserFollow(DoneeModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name='user') #follower user
    follow_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name = 'follow_user') #followed user
    is_followed = models.BooleanField(default=False)
    

    class Meta:
        verbose_name = 'UserFollow'
        verbose_name_plural = 'UserFollows'
        db_table = 'user_follow'

    def __str__(self):
        return self.follow_user.username

class ProfileFollow(DoneeModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name='user_user') #follower user
    follow_profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name = 'follow_profile') #followed profile
    is_followed = models.BooleanField(default=False)
    

    class Meta:
        verbose_name = 'ProfileFollow'
        verbose_name_plural = 'ProfileFollows'
        db_table = 'profile_follow'

    def __str__(self):
        return self.follow_profile.username


class NgoUserRole(DoneeModel):
    ROLE_TYPES=(('SUPERADMIN', 'SuperAdmin'),
        ('ADMIN', 'Admin'),
        ('EDITOR', 'Editor'),
        ('DONEEINVITOR','DoneeInvitor'),
        ('ACCOUNTANT','Accountant')
        )
    role_type = models.CharField(max_length=30, blank=False, null=False,
                                     choices=ROLE_TYPES)
    
    class Meta:
        verbose_name = 'NgoUserRole'
        verbose_name_plural = 'NgoUserRoles'
        db_table = 'ngo_user_role'
    
    
class NgoUser(DoneeModel):
    role = models.ForeignKey(NgoUserRole, on_delete=models.PROTECT, related_name='role_ngo_user')
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='role_profile') 
    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name='user_ngo_user')
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together=('user','profile')
        verbose_name = 'NgoUser'
        verbose_name_plural = 'NgoUsers'
        db_table = 'ngo_user'
    
    def __str__(self) :
        return self.profile.username


class PlatformUserRole(DoneeModel):
    ROLE_TYPES = (('ADMIN', 'Admin'),
                  ('EDITOR', 'Editor'),
                  ('DONEEINVITOR', 'DoneeInvitor'),
                  ('ACCOUNTANT', 'Accountant')
                  )
    role_type = models.CharField(max_length=30, blank=False, null=False,
                                 choices=ROLE_TYPES)

    class Meta:
        verbose_name = 'Platform User Role'
        verbose_name_plural = 'Platform User Roles'
        db_table = 'platform_user_roles'


class PlatformUser(DoneeModel):
    role = models.ForeignKey(PlatformUserRole, on_delete=models.PROTECT, related_name='role_platform_user')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='platform_user')
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Platform User'
        verbose_name_plural = 'Platform Users'
        db_table = 'platform_users'

    def __str__(self):
        return self.user.username

