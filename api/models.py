from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):

        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email), **kwargs)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **kwargs):

        user = self.create_user(email, password=password, **kwargs)
        user.role = "admin"
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    USER_ROLES = (
        ("user", "user"),
        ("moderator", "moderator"),
        ("admin", "admin"),
    )
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True,
    )
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    username = models.SlugField(unique=True, blank=True, null=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default=1)
    objects = UserManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class Categories(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    category = models.ForeignKey(
        Categories, on_delete=models.SET_NULL, blank=True, null=True
    )
    genre = models.ForeignKey(Genres, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(Titles, on_delete=models.CASCADE, related_name="reviews")
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    score = models.IntegerField(
        default=0, validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True, db_index=True)


class Comments(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    pub_date = models.DateTimeField("Дата добавления", auto_now_add=True, db_index=True)
