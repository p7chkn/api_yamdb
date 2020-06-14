from django.db import models
from django.contrib.auth.models import (
 BaseUserManager, AbstractBaseUser
)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):

        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
                    email=self.normalize_email(email),
                    **kwargs
                     )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):

        user = self.create_user(
                    email,
                    password=password, 
                    **kwargs              
                    )
        user.role = 'admin'
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    USER_ROLES = (
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    )
    email = models.EmailField(verbose_name='email address',
                              max_length=255,
                              unique=True,
                              )
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    username = models.SlugField(unique=True, blank=True, null=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default=1)    
    objects = UserManager()    
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
