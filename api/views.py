import concurrent.futures
import datetime
import json

import requests
from bs4 import BeautifulSoup
import re
import boto3
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

def index():
    return HttpResponse("Hello World!")


def test(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        url_ = body['url']
        regex_ = body['regex']

        news_tags_ = body['news_tags']
        news_attributes_ = body['news_attributes']
        news_id_ = body['news_id']

        desc_tag_ = body['desc_tag']
        desc_attribute_ = body['desc_attribute']
        desc_id_ = body['desc_id']

        title_tag_ = body['title_tag']

        sample_news_url_ = body['sample_news_url']

        error_code = {'main link': 'found','news': 'found' ,'title': 'found', 'description': 'found', 'status': 'success'}
        # Check if the url exists
        try:
            r = requests.get(url_)
            html = r.content

            try:
                r = requests.get(sample_news_url_)
                html = r.content
            except requests.exceptions.ConnectTimeout:
                return
            try:
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
                    error_code['description'] = 'not found'

                img = latest.find('img')

                try:
                    title = (latest.find(title_tag_)).get_text()
                except:
                    error_code['title'] = 'not found'

            except:
                error_code = {'main link': 'found', 'news': 'not found', 'title': 'na', 'description': 'na'}

        except:
            error_code = {'main link': 'not found', 'news': 'na', 'title': 'na', 'description': 'na'}

        if error_code['main link'] == 'found' and error_code['title'] == 'found' and error_code['description'] == 'found':
            error_code['status'] = 'success'
        else:
            error_code['status'] = 'failure'

        return JsonResponse(error_code)