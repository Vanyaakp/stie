from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=100)
    curator = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Club(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Student(models.Model):
    first_name = models.CharField(max_length=100)   # имя
    last_name = models.CharField(max_length=100)    # фамилия
    age = models.IntegerField()                     # возраст
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    clubs = models.ManyToManyField(Club, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UserProfile(models.Model):
    """Профиль пользователя с аватаром"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profile_avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, default='')
    
    def __str__(self):
        return f"Профиль {self.user.username}"
    
    def get_avatar_url(self):
        """Возвращает URL аватара или placeholder"""
        if self.avatar:
            return self.avatar.url
        return f"https://ui-avatars.com/api/?name={self.user.first_name}+{self.user.last_name}&background=667eea&color=fff&bold=true&size=200"