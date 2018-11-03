from django.db import models
import django.utils.timezone as timezone
from useraction.models import User


class Competition(models.Model):
    name = models.CharField(max_length=32, blank=False)
    subject = models.CharField(max_length=10, blank=False)
    group_size = models.IntegerField(default=1)
    enroll_start = models.DateTimeField(default=timezone.now)
    enroll_end = models.DateTimeField(default=timezone.now)
    detail = models.TextField(default='')
    procedure = models.TextField(default='')
    url = models.URLField(default='')
    charge = models.IntegerField(default=0)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)
    publisher = models.ForeignKey(User, on_delete=models.PROTECT, related_name='published_competitions')
    judges = models.ManyToManyField(User, related_name='judge_in_competitions')

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'groupSize': self.group_size,
            'enrollStart': self.enroll_start,
            'enrollEnd': self.enroll_end,
            'detail': self.detail,
            'procedure': self.procedure,
            'url': self.url,
            'charge': self.charge,
            'upvote': self.upvote,
            'downvote': self.downvote,
            'publisher': self.publisher.username
        }


class Notice(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE)
    posted_time = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=False)

    def __str__(self):
        return f'{self.competition}: {self.content}'

    def to_dict(self):
        return {
            'competitionId': self.competition.id,
            'competitionName': self.competition.name,
            'postedTime': self.posted_time,
            'content': self.content
        }


class Group(models.Model):
    name = models.CharField(max_length=32, blank=False)
    competition = models.ForeignKey(Competition, on_delete=models.PROTECT)
    leader = models.ForeignKey(User, on_delete=models.PROTECT, related_name='lead_in_competitions')
    members = models.ManyToManyField(User, related_name='attended_competitions')
    commit_path = models.FilePathField(blank=True)
    rank = models.TextField()

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'competitionId': self.competition.id,
            'competitionName': self.competition.name,
            'leaderName': self.leader.username,
            'membersName': [member.username for member in self.members.all()],
            'commitPath': self.commit_path,
            'rank': self.rank
        }
