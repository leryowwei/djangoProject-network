from django.contrib import admin
from .models import User, Follower, Post, Like

# all other models
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password')


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'pub_date', 'post')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')