from django.db import models
from django.utils import timezone
# Create your models here.
class Polls(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    option1 = models.CharField(max_length=200, default='Option 1')
    option2 = models.CharField(max_length=200, default='Option 2')

    def __str__(self):
        return self.question
    def published(self):
        return self.pub_date <= timezone.now()
        