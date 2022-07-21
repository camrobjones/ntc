"""
NTC Database Models
-------------------
Database ORM to store models

Profile: User profile info
Topic: Topics to be normed
Vote: User votes on topics
Comment: Talk about topics
CommentVote: Up/downvotes for topics

Attributes
----------
CATEGORIES : tuple
    Description
User : TYPE
    Description
"""

from django.db import models
from django.utils import timezone as tz
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Create your models here.


class Profile(models.Model):
    """Store NTC-specific info about users

    Attributes
    ----------
    user : User
        One-to-One relation to User model
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="ntc_profile"
    )
    created = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='ntc/', default="ntc/default.svg")

    @property
    def votes(self):
        """List of dicts of vote data for user"""
        out = [v.data for v in self.vote_set.all()]
        return out

    @property
    def data(self):
        """Serializable data about Profile"""
        out = {"username": self.user.username,
               "created": self.created.isoformat(),
               "last_active": self.last_active.isoformat(),
               "votes": self.votes,
               "image": self.image.url,
               "guest": self.user.guest}
        return out


class Tag(models.Model):
    """Tags for searching and organising topics

    Attributes
    ----------
    created : tz.datetime
        Creation timestamp
    name : str
        Name of the topic
    profile : ntc.models.Profile
        Creator of the tag
    """

    name = models.CharField(max_length=50, unique=True)

    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)

    created = models.DateTimeField(auto_now_add=True)


class Topic(models.Model):
    """Topics to be normed!

    Attributes
    ----------
    category : str
        High level category of the topic
    created : tz.datetime
        Creation timestamp
    description : str
        Info about topic (max 1000 char)
    name : str
        Name of topic (max 50 char)
    profile : ntc.models.Profile
        Creator of topic
    slug : str
        URL slug for topic (unique)
    tags : iterable of ntc.models.Tag
        Tags associated with the topic
    url : str
        URL with more info about topic (optional)
    verified : bool
        Has the topic been verified?
    """

    class Categories(models.TextChoices):
        """High-level categories for topics"""
        PERSON = "PER", _("Person")
        POLICY = "POL", _("Policy")
        GOVERNMENT = "GOV", _("Government")
        COUNTRY = "COU", _("Country")
        PHILOSOPHY = "PHI", _("Philosophy")
        WORK = "WOR", _("Work")
        OTHER = "OTH", _("Other")

    name = models.CharField(max_length=50)

    slug = models.SlugField(max_length=60, unique=True)

    description = models.CharField(max_length=1000)

    category = models.CharField(
        max_length=3,
        choices=Categories.choices)

    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)

    created = models.DateTimeField(auto_now_add=True)

    url = models.URLField(blank=True, null=True, default="")

    verified = models.BooleanField(default=False)

    tags = models.ManyToManyField(
        Tag)

    @classmethod
    def check_slug(cls, slug):
        """Check slug is unique. If not alter and return unique slug"""
        objects = cls.objects.filter(slug=slug)

        if not objects.exists():
            return slug

        objects = cls.objects.filter(slug__startswith=slug)
        slug = f"{slug}_{objects.count()}"

        # Double check slug is unique
        objects = cls.objects.filter(slug=slug)

        if not objects.exists():
            return slug

        return self.id


class Vote(models.Model):
    """Profile vote on topic location

    Attributes
    ----------
    created : datetime
        Creation timestamp
    profile : ntc.models.Profile
        Profile of voter
    topic : ntc.models.Topic
        Topic being voted on
    updated : datetime
        Last edit timestamp
    x : float
        x co-ordinate of vote (-10 < x < 10)
    y : float
        x co-ordinate of vote (-10 < y < 10)
    """

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE
    )

    x = models.FloatField()

    y = models.FloatField()

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)

    @property
    def data(self):
        """Dict of vote data"""
        out = {"topic": self.topic.id,
               "topic_name": self.topic.name,
               "profile": self.profile.id,
               "x": self.x,
               "y": self.y,
               "updated": self.updated.isoformat()}
        return out


class Skip(models.Model):
    """Profile vote on topic location

    Attributes
    ----------
    created : datetime
        Creation timestamp
    profile : ntc.models.Profile
        Profile of voter
    topic : ntc.models.Topic
        Topic being voted on
    updated : datetime
        Last edit timestamp
    """

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE
    )

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    """User comments on topics

    Attributes
    ----------
    created : datetime
        Creation timestamp
    edited : datetime
        Last edit timestamp
    parent : self
        Parent comment in thread (optional)
    profile : ntc.models.Profile
        Profile of commenter
    score : int
        Total of all votes
    text : str
        Text of comment
    topic : ntc.models.Topic
        Topic being commented on
    """

    profile = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,  # Prevent comment delete cascade
        null=True,
        blank=True)

    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE)

    parent = models.ForeignKey(
        "self",
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        default=None)

    score = models.IntegerField(
        default=0)

    text = models.TextField()

    created = models.DateTimeField(auto_now_add=True)

    edited = models.DateTimeField(default=tz.now)

    def vote_count(self):
        """Sum commentvotes"""
        score = self.commentvote_set.aggregate(models.Sum('value'))
        self.score = score['value__sum'] or 0


class CommentVote(models.Model):
    """User vote on a comment

    Attributes
    ----------
    comment : ntc.models.Comment
        Comment being voted on
    created : datetime
        Creation timestamp
    profile : ntc.models.Profile
        Profile of comment voter
    updated : datetime
        Last updated timestamp
    value : int {-1,1}
        Upvote or downvote?
    }
    """

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE)

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE)

    class VoteValue(models.IntegerChoices):
        UP = 1, _('Upvote')
        DOWN = -1, _('Downvote')

    value = models.IntegerField(
        choices=VoteValue.choices)

    created = models.DateTimeField(auto_now_add=True)

    updated = models.DateTimeField(auto_now=True)
