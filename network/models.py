from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass

    def __str__(self):
        return '{}'.format(self.username)


class Follower(models.Model):
    # follower is the one following the user
    # following is the people following the user
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'following')

    class Meta:
        # per user can only follow the same user once
        unique_together = (('follower', 'following'))
    
    def __str__(self):
        return '{} following {}'.format(self.follower, self.following)

    def clean(self):
        if self.follower.username == self.following.username:
            raise ValidationError('Follower and following cannot be the same person {}'.format(self.follower))

    def serialise(self):
        return {
            "follower": self.follower.username,
        }



class Like(models.Model):
    """ Like post """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'react_user')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name = 'react_post')

    class Meta:
        # make sure that a user can only create one entry per post
        unique_together = (('user', 'post'))
    
    def __str__(self):
        return '{},  {}'.format(self.user, self.post)
    
    def serialise(self):
        return {
            "user": self.user.username,
        }


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'author')
    pub_date = models.DateTimeField()
    post = models.TextField(blank=False, null=False)

    def __str__(self):
        return 'Author: {}, Published on: {}'.format(self.author, self.pub_date)