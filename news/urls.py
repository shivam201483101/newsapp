from django.urls import path
from news.views import scrape, news_list,about,contact,breakinghome,run,newui

urlpatterns = [
  path('scrape/<str:name>', scrape, name="scrape"),
  path('', news_list, name="home"),
  path('about/', about, name='about'),
  path('contact/', contact, name='contact'),
  path('newui/', newui, name='newui'),  
  path('run/', run, name='run'),
   
  path('', breakinghome, name="breakinghome"),
]