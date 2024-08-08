from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings

class EmployeeManager(BaseUserManager):
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class Employee(AbstractUser):

    no_space_validator = RegexValidator(
        regex=r'^[A-Za-z_]+$',
        message='This field should only contain letters,with no spaces.'
    )

    first_name = models.CharField(max_length=30, validators=[no_space_validator])
    last_name = models.CharField(max_length=30, validators=[no_space_validator])
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = None
    objects = EmployeeManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS=[]
    
    class Meta:
        verbose_name = 'employee'
        verbose_name_plural = 'employees'    

class ProjectDetails(models.Model):
    
    no_space_validator = RegexValidator(
        regex=r'^[A-Za-z_]+$',
        message='This field should only contain letters and underscores, with no spaces.'
    )
    description_validator = RegexValidator(
        regex=r'^[A-Za-z0-9\s.,;:!?()-]*$',
        message='Description can contain letters, numbers, spaces, and basic punctuation.'
    )
    no_special_char_validator = RegexValidator(
        regex=r'^[A-Za-z ]+$',
        message='Status can only contain letters and spaces.'
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[no_space_validator]
    )
    description = models.TextField(validators=[description_validator])
    start_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    status = models.CharField(max_length=50,validators=[description_validator])
    estimated_span_in_days = models.IntegerField(default=0)
    employees = models.ManyToManyField(Employee, related_name='projects') 


class AccessToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)