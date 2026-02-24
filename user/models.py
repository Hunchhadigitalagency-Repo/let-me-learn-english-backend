from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.utils.text import slugify

USER_TYPE_CHOICES = (
    ('superadmin', 'Super Admin'),
    ('admin', 'Admin'),
    ('parent', 'Parent'),
    ('student', 'Student'),
    ('school', 'School'),
)

class User(AbstractUser):
    email = models.EmailField(unique=True)
   
    login_code = models.CharField(max_length=6, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    
    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES,null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    is_disabled = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    google_id = models.CharField(max_length=255, blank=True, null=True)
    google_avatar = models.URLField(blank=True, null=True)
    is_active=models.BooleanField(default=True)
    
    grade=models.CharField(max_length=255,null=True,blank=True)
    section=models.CharField(max_length=255,null=True,blank=True)
    dateofbirth=models.DateTimeField(null=True,blank=True)
    student_parent_name=models.CharField(max_length=255,null=True,blank=True)
    student_parent_email=models.EmailField(null=True,blank=True)
    student_parent_phone_number=models.CharField(null=True,blank=True)
    
    

    def __str__(self):
        return f"{self.user.email} Profile"
    
class Parent(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True
    )


    # For non-registered parents
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.student:
            return f"{self.student.email} → {self.email}"
        return f"{self.name} → {self.email}"

class ResetPassword(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    TOKEN_EXPIRY_MINUTES = 15 

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=self.TOKEN_EXPIRY_MINUTES)

    def __str__(self):
        return f"Reset token for {self.user.username}"

class Country(models.Model):
    name=models.CharField(max_length=255)
    
    def __str__(self):
        return self.name
    
    
class Province(models.Model):
    name=models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
class District(models.Model):
    name=models.CharField(max_length=255)
    province=models.ForeignKey(Province,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
    

class School(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255) 
    establish_date = models.DateField(null=True, blank=True)
    landline = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District,on_delete=models.SET_NULL, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    code=models.CharField(blank=True,null=True,unique=True)
    logo=models.FileField(upload_to='schoollogo/',null=True,blank=True)
    
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.code and self.name and self.establish_date:
            base_code = f"{slugify(self.name)}-{self.establish_date.year}"
            code = base_code
            counter = 1

           
            while School.objects.filter(code=code).exists():
                code = f"{base_code}-{counter}"
                counter += 1

            self.code = code

        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    
    
    
class SchoolStudentParent(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_school_relations',  
        limit_choices_to={'userprofile__user_type': 'student'}
    )
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='parent_school_relations', 
        limit_choices_to={'userprofile__user_type': 'parent'}
    )

    class Meta:
        unique_together = ('student', 'school', 'parent')

    def __str__(self):
        return f"{self.student.email} - {self.parent.email} @ {self.school.name}"


class FocalPerson(models.Model):
    name=models.CharField(max_length=255)
    phone=models.CharField(max_length=255)
    email=models.EmailField(max_length=255)
    designation=models.CharField(max_length=255)
    school=models.ForeignKey(School,on_delete=models.CASCADE)
    
    
from django.db import models
from django.contrib.auth.models import Group
    
class CustomRole(models.Model):
    user = models.ManyToManyField(User, related_name='roles', blank=True)
    role = models.CharField(max_length=250, blank=True, null=True)
    group = models.OneToOneField(Group, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    
    def __str__(self):
        return f"{self.role or 'No Role'}"
    
    
class CustomPermissionClass(models.Model):
    name = models.CharField(blank=True, null=True, max_length=250)
    role = models.ForeignKey(CustomRole, on_delete=models.CASCADE, related_name='permissions')
    
    def __str__(self):
        return f"Permission: {self.name or 'Unnamed'} (Role: {self.role})"