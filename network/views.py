from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from .models import User, Post, Like, Follower
from datetime import datetime
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['post']


def paginate_post(request, filter_on=False, filter_user=None, posts_per_page=10):
    if filter_on:
        posts = []
        for x in filter_user:
            posts += Post.objects.filter(author=x).order_by('-pub_date')
    else:
        posts = Post.objects.all().order_by('-pub_date')

    paginator = Paginator(posts, posts_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj


def index(request):
    # paginate all posts
    page_obj = paginate_post(request)

    return render(request, "network/index.html", {'page_obj': page_obj})


def get_profile_page(request, username):
    # get profile user
    user = User.objects.filter(username=username)

    # get request user
    request_user = User.objects.filter(username=request.user.get_username())

    # paginate all posts
    page_obj = paginate_post(request, filter_on=True, filter_user=user)

    # get no of followers and how many following
    followers = Follower.objects.filter(following=user[0])
    following = Follower.objects.filter(follower=user[0])

    # check if request user is following the profile user or not
    is_following = False
    for follower in followers:
        if follower.follower.username == request.user.get_username():
            is_following = True
            break

    return render(request, "network/profile.html", {
        'profile': username,
        'page_obj': page_obj,
        'followers': followers,
        'following': following,
        'is_following': is_following,
        })
 

def new_post(request):
    # get empty form  
    form = PostForm()

    if request.method == 'POST':
        filled_form = PostForm(request.POST)
        if filled_form.is_valid():
            filled_form.instance.author = User.objects.filter(username=request.user.get_username())[0]
            filled_form.instance.pub_date = datetime.today()
            filled_form.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/new.html", {'form': filled_form})
    else:
        return render(request, "network/new.html", {'form': form})    


def get_like_count(request, post_id):
    likes = Like.objects.filter(post=Post.objects.filter(id=post_id)[0])

    arr_likes = [email.serialise() for email in likes]

    # find out whether user liked the post provided they are login
    if request.user.is_authenticated:
        user_like = likes.filter(user=User.objects.filter(username=request.user.get_username())[0])
        reaction = True if user_like else False
        is_authenticated = True
    else:
        reaction = False
        is_authenticated = False

    return JsonResponse({
        "count": arr_likes,
        "reaction": reaction,
        "isAuthenticated": is_authenticated,
        }, safe=False)


def get_following_posts(request):
    # find out people that user is following and save all user instances in list
    user = User.objects.filter(username=request.user.get_username())[0]
    following = []
    for x in Follower.objects.filter(follower=user):
        following.append(x.following)

    # paginate all posts
    page_obj = paginate_post(request, filter_on=True, filter_user=following)

    return render(request, "network/following.html", {'page_obj': page_obj})


@csrf_exempt
def update_like(request):
    # update like or unlike
    if request.method == "POST":
        # load data based on api json input
        data = json.loads(request.body)
        post_id = data.get("postId")
        reaction = data.get("method")
        post = Post.objects.filter(id=post_id)[0]
        user = User.objects.filter(username=request.user.get_username())[0]
        if reaction == "Like":
            try:
                like = Like(post = post, user = user)
                like.full_clean()
                like.save()
            except ValidationError:
                return JsonResponse({"error": "Error saving like reaction to database."}, status=400)
        else:
            Like.objects.filter(post = post, user = user).delete()
        
        return JsonResponse({
            "Success": "{} for Post {} updated".format(reaction, post_id)
            }, status=200)

    else:
        return JsonResponse({"error": "POST request required."}, status=400)


@csrf_exempt
def update_post(request):
    # update like or unlike
    if request.method == "PUT":
        # load data based on api json input
        data = json.loads(request.body)
        post_id = data.get("postId")
        content = data.get("content")
        post = Post.objects.filter(id=post_id)[0]
        user = User.objects.filter(username=request.user.get_username())[0]

        # update post and make sure user is the author
        if post.author == user:
            post.post = content

            try:
                post.full_clean()
                post.save()
            except ValidationError:
                return JsonResponse({"error": "Error saving your update. Please check your input."}, status=400)

            return JsonResponse({
                "Success": "Post {} updated".format(post_id)
                }, status=200)
        else:
            return JsonResponse({"error": "Only author is allowed to edit their own post"}, status=400)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)


@csrf_exempt
def follow_user(request):
    if request.method == "POST":
        # load data based on api json input
        data = json.loads(request.body)
        trigger = data.get("trigger")
        profile_name = data.get("profile")
        profile_user = User.objects.filter(username=profile_name)[0]
        request_user = User.objects.filter(username=request.user.get_username())[0]

        if trigger:
            try:
                follower = Follower(follower=request_user, following=profile_user)
                follower.full_clean()
                follower.save()
                arr_followers = [x.serialise() for x in Follower.objects.filter(following=profile_user)]
                return JsonResponse({
                    "Success": "{} following {}".format(request_user, profile_user),
                    "followers": arr_followers,
                    }, status=200)

            except ValidationError:
                return JsonResponse({"error": "Error with follow function. Please try again"}, status=400)
        else:
            Follower.objects.filter(follower=request_user, following=profile_user).delete()

            # if no followers we need to capture the error
            arr_followers = [x.serialise() for x in Follower.objects.filter(following=profile_user)]

            return JsonResponse({
                "Success": "{} unfollowed {}".format(request_user, profile_user),
                "followers": arr_followers,
                }, status=200)
    else:
        return JsonResponse({"error": "POST request required."}, status=400)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
