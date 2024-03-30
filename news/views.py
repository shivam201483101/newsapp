from django.shortcuts import render
import requests
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup as BSoup
from news.models import Headline


from news.models import NewsArticle
from newspaper import Article
import nltk
from  gnews import GNews

import datetime
from django.utils import timezone
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime
import pytz
# import torch
# from transformers import BertModel, BertTokenizer

# from summarizer import Summarizer

from transformers import T5Tokenizer, T5ForConditionalGeneration

# Initialize the tokenizer and model
tokenizer = T5Tokenizer.from_pretrained('t5-small',legacy=False)
model = T5ForConditionalGeneration.from_pretrained('t5-small')
nltk.download('vader_lexicon')

# tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
# model = BertModel.from_pretrained('bert-base-uncased')



def run(request):
    NewsArticle.objects.all().delete()
    category = request.GET.get('category')
    topic = request.GET.get('topic')
    search_topic=request.GET.get('searchTopic')
    no_of_news = int(request.GET.get('no', 5))
    #print(category,topic,no_of_news,search_topic)   
   

    if category == 'Trending':
        news_list = fetch_top_news(no_of_news)
    elif category == 'Favourite' and topic:
        news_list = fetch_category_news(topic,no_of_news)
    elif category == 'Search':
        news_list = fetch_news_search_topic(search_topic,no_of_news)
    else:
        news_list = [] 
        
    for item in news_list:
        
        
        sentiment, image, summary = extract_and_summarize(item['url'])
        if not image:
            image_url ="https://www.alamy.com/blog/wp-content/uploads/2016/11/E4G70X-1024x683.jpg"
        else:
            image_url = image
        
        published_date=item['published date']
        if not item['published date']:
            published_date = datetime.now()
        
        date_object = datetime.strptime(published_date, "%a, %d %b %Y %H:%M:%S GMT")
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_date_object = date_object.replace(tzinfo=pytz.utc).astimezone(ist_timezone)

        
        #print(summary,sentiment,image,image_url,item['published date'],date_object,ist_date_object)
        neww=NewsArticle(
                title=item['title'],
                image=image,
                url=item['url'],
                content=item['publisher']['href'],
                summary=summary,
                created_at=date_object,
                sentiment=sentiment
            )
        neww.save()   
      
    return newui(request)


def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    if sentiment_scores['compound'] >= 0.05:
        sentiment = 'positive'
    elif sentiment_scores['compound'] <= -0.05:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    return sentiment   

def extract_and_summarize(article_url):
    # Extract content
    article = Article(article_url)
    article.download()
    article.parse()
    
    # Summarize content
    summary = summarize_with_t5(article.text)
    sentiment= analyze_sentiment(summary)
    
    return sentiment, article.top_image, summary
  
def summarize_with_t5(text):
    # Prepend the prompt to the text
    input_text = "summarize: " + text

    # Encode the input text
    input_ids = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True)

    # Generate the summary
    summary_ids = model.generate(input_ids, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    
    # Decode and return the summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return summary

# def summarize_with_bert(text):
    

#     # Tokenize the text
#     inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True)

#     # Generate summary
#     with torch.no_grad():
#         outputs = model(**inputs)

#     # Summarize using the hidden states
#     summary = ' '.join(tokenizer.decode(output, skip_special_tokens=True) for output in outputs[0].squeeze())

#     return summary

def fetch_news_search_topic(topic,no):
    try:
        google_news = GNews(language='en',
        period='6m', start_date=None, end_date=None,
        max_results=no, exclude_websites = ['yahoo.com', 'msn'] )
        news_by_topic = google_news.get_news(topic)

        return news_by_topic
    except Exception as e:
        print(f"Error fetching search topic news: {e}")
        return []

def fetch_top_news(no):
    try:
        google_news = GNews(language='en', country='IN', period='1m',
        start_date=None, end_date=None, max_results=no)
        top_news = google_news.get_top_news()
        return top_news
    
    except Exception as e:
        print(f"Error fetching category news: {e}")
        return []

def fetch_category_news(topic,no):
    try:
        google_news = GNews(language='en', 
        period='1m', start_date=None, end_date=None,
        max_results=no, exclude_websites = ['yahoo.com', 'msn'] )
        news_by_topic = google_news.get_news_by_topic(topic)

        return news_by_topic
    except Exception as e:
        print(f"Error fetching category news: {e}")
        return []

 
    

def scrape(request, name):
    Headline.objects.all().delete()
    session = requests.Session()
    session.headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
    url = f"https://www.theonion.com/{name}"
    content = session.get(url).content
    soup = BSoup(content, "html.parser")

    News = soup.find_all("div", {"class": "sc-cw4lnv-13 hHSpAQ"})
    count=0
    for article in News:
        count=count+1

        if count<=12:
            main = article.find_all("a", href=True)

            linkx = article.find("a", {"class": "sc-1out364-0 dPMosf js_link"})
            link = linkx["href"]

            titlex = article.find("h2", {"class": "sc-759qgu-0 cvZkKd sc-cw4lnv-6 TLSoz"})
            title = titlex.text

            imgx = article.find("img")["data-src"]

            new_headline = Headline()
            new_headline.title = title
            new_headline.url = link
            new_headline.image = imgx
            new_headline.save() ##saving each record to news_headline
    return redirect("../")

def breakinghome(request):
    Headline.objects.all().delete()
    session = requests.Session()
    session.headers = {"User-Agent": "Googlebot/2.1 (+http://www.google.com/bot.html)"}
    url = f"https://www.theonion.com/latest"
    content = session.get(url).content
    soup = BSoup(content, "html.parser")

    News = soup.find_all("div", {"class": "sc-cw4lnv-13 hHSpAQ"})
    count=0
    for article in News:
        count=count+1

        if count<=8:
            main = article.find_all("a", href=True)

            linkx = article.find("a", {"class": "sc-1out364-0 dPMosf js_link"})
            link = linkx["href"]

            titlex = article.find("h2", {"class": "sc-759qgu-0 cvZkKd sc-cw4lnv-6 TLSoz"})
            title = titlex.text

            imgx = article.find("img")["data-src"]

            new_headline = Headline()
            new_headline.title = title
            new_headline.url = link
            new_headline.image = imgx
            new_headline.save() ##saving each record to news_headline
    
    headlines = Headline.objects.all()[::-1]
    context = {
        "object_list": headlines,
    }

    return render(request, "home.html", context)

def news_list(request):
    #fetching records stored in Headline model
    headlines = Headline.objects.all()[::-1]#store records in reverse order
    news = {
        "object_list": headlines,}
    return render(request, "home.html", news)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def newui(request):
    articles = NewsArticle.objects.all()[::-1]#store records in reverse order
    news = {
        "article_list": articles,}
    # Add your scraping logic here based on the inputs
    return render(request, 'newui.html', news)







# context is a dictionary using which we can pass values to templates from views
