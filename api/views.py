import json
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponse
import tweepy


def index():
    return HttpResponse("Hello World!")


def test(request):
    if request.method == 'POST':
        decoded_data = request.body.decode('utf-8-sig')
        decoded_data.replace('{[', '[')
        decoded_data.replace(']}', ']')
        body = json.loads(decoded_data)
        scrap_type = body["scrap_type"]
        if scrap_type == 1:
            url_ = body["url"]
            regex_ = body["regex"]

            news_tags_ = body["news_tags"]
            news_attributes_ = body["news_attributes"]
            news_id_ = body["news_id"]

            desc_tag_ = body["desc_tag"]
            desc_attribute_ = body["desc_attribute"]
            desc_id_ = body["desc_id"]

            title_tag_ = body["title_tag"]

            sample_news_url_ = body["sample_news_url"]

            error_code = {"mainlink": "found", "news": "found","title": "found", "description": "found", "status": True}
            # Check if the url exists
            try:
                r = requests.get(url_)
                html = r.content

                try:
                    r = requests.get(sample_news_url_)
                    html = r.content
                    soup = BeautifulSoup(html, "lxml")

                    # Check what values are given for news
                    # Only tag
                    if (news_attributes_ is None) and (news_id_ is None):
                        latest = soup.find(news_tags_)

                    # Only class
                    elif (news_attributes_ is not None) and (news_id_ is None):
                        latest = soup.find(news_tags_, class_=news_attributes_)

                    # Only id
                    elif (news_attributes_ is None) and (news_id_ is not None):
                        latest = soup.find(news_tags_, id=news_id_)

                    # Both, class and id are given
                    else:
                        latest = soup.find(news_tags_, class_=news_attributes_, id=news_id_)

                    try:
                        # Check what values are given for desc
                        # Only tag
                        if (desc_attribute_ is None) and (desc_id_ is None):
                            description = (latest.find(desc_tag_)).get_text()

                        # Only class
                        elif (desc_attribute_ is not None) and (desc_id_ is None):
                            description = (latest.find(desc_tag_, class_=desc_attribute_)).get_text()

                        # Only id
                        elif (desc_attribute_ is None) and (desc_id_ is not None):
                            description = (latest.find(desc_tag_, id=desc_id_)).get_text()

                        # Both, class and id are given
                        else:
                            description = (latest.find(desc_tag_, class_=desc_attribute_, id=desc_id_)).get_text()

                    except AttributeError:
                        error_code["description"] = "not found"

                    img = latest.find('img')

                    try:
                        title = (latest.find(title_tag_)).get_text()
                    except:
                        error_code["title"] = "not found"

                except Exception as e:
                    error_code = {"mainlink": "found", "news": "not found", "title": "na", "description": "na"}

            except:
                error_code = {"mainlink": "not found", "news": "na", "title": "na", "description": "na"}

            if error_code["mainlink"] == "found" and error_code["news"] == "found" and error_code["title"] == "found" and error_code["description"] == "found":
                error_code["status"] = True
            else:
                error_code["status"] = False

            return JsonResponse(error_code)

        if scrap_type == 3:
            url_ = body["url"]
            error_code = {"twitter_handle": "found", "status": True}
            TWITTER_CONSUMER_KEY = "6vS6tTlBo87cl38emLHtc8CVS"
            TWITTER_SECRET_KEY = "ctf0Lcj9sfprh7pz0J0yqIi4lmOUk3dAg9VzFnuVQtzJVKgclS"
            TWITTER_ACCESS_TOKEN = "1270719106304499715-6P5FGEuWxETchBk3BDbaEaHkimE8v6"
            TWITTER_ACCESS_TOKEN_SECRET = "AVaLSQ4qRdPNVyNiV29DxdVupMVGDgg2uh7T3Ny20Zjcm"

            auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_SECRET_KEY)
            auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth)

            # tweets = tweepy.Cursor(api.user_timeline, screen_name=user, tweet_mode='extended').items(100)
            try:
                tweets = api.user_timeline(screen_name=url_, count=50, tweet_mode='extended')
                count = 0
                for t in tweets:
                    try:
                        if t.entities['urls'][0]['expanded_url'] is not None or t.entities['urls'][0]['url'] is not None:
                            title = t.full_text
                            if title is not None:
                                count = count+1
                        else:
                            pass
                    except:
                        pass

                if count == 0:
                    error_code = {"twitter_handle": "not found", "status": False}
            except:
                error_code = {"twitter_handle": "not found", "status": False}

            return JsonResponse(error_code)

        if scrap_type == 2:
            url_ = body["url"]
            error_code = {"rss_feed_link": "found", "status": True}
            count = 0
            try:
                r = requests.get(url_)
                html = r.content
                soup = BeautifulSoup(html, "html.parser")
                item = soup.find_all("item")

                for i in item:
                    try:
                        title = i.title.text
                        count = count+1
                    except:
                        title = None
            except requests.exceptions.ConnectTimeout:
                error_code = {"rss_feed_link": "not found", "status": False}

            if count == 0:
                error_code = {"rss_feed_link": "not found", "status": False}

            return JsonResponse(error_code)
