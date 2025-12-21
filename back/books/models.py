from django.db import models
from django.conf import settings
class Book(models.Model):
    title = models.CharField( max_length=200)
    author =models.CharField( max_length=200)
    description =models.TextField(blank=True)
    cover_url = models.URLField(blank=True)
    category= models.CharField(max_length=200, blank=True)
    created_at= models.DateField(auto_now_add=False)

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=50)
    birth_date = models.DateField()

    # ✅ 추가
    bookti_code = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"
