from django.db import models


class Headline(models.Model):
  title = models.CharField(max_length=200)#title char(200)
  image = models.URLField(null=True, blank=True)#image
  url = models.TextField()
  
  def __str__(self):
    return self.title
  
class NewsArticle(models.Model):
    title = models.CharField(max_length=200)
    image = models.URLField(null=True, blank=True)
    url = models.URLField()
    content = models.TextField()
    summary = models.TextField()
    sentiment = models.TextField(default='neutral')
    created_at = models.DateTimeField()

    def __str__(self):
        return self.title