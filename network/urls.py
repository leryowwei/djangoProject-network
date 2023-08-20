
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("newPost", views.new_post, name="newPost"),
    path("following", views.get_following_posts, name="following"),
    path("profile/<str:username>", views.get_profile_page, name="profile"),

    # API Routes
    path("likeCount/<int:post_id>", views.get_like_count, name="get_like_count"),
    path("updateLike", views.update_like, name="upate_like"),
    path("updatePost", views.update_post, name="update_post"),
    path("followUser", views.follow_user, name="follow_user"),
]
