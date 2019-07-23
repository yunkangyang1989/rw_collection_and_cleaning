"""
v1 version of colelction and cleaning methods for political bias paper
"""
import requests
import datetime
import os
import newspaper
import tqdm
import re
import urllib.request
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


def get_full_html(url, method_2=False):
    """
    method to obtain a web pages entire html contents
    :param url:
    :param method_2: boolean, if true append clear this page
    :return: html
    """
    try:
        url = 'https://clearthis.page/?u=' + url if method_2 else url
        html = urllib.request.urlopen(url).read()
    except Exception as e:
        html = e
    return html


def article_data_frame(sf, save_file):
    """
    method 1 for downloading articles and storing in a new data frame
    :param sf: a data frame loaded from a csv gathered from media cloud
    :param save_file:
    :return: None
    """
    df = pd.DataFrame(columns=['publish_date', 'url', 'title', 'authors', 'media_site', 'article'])
    # fill data frame
    for idx in range(len(sf)):
        # data reproduced from mdeia cloud csv
        date = sf['publish_date'][idx]
        url = sf['url'][idx]
        title = sf['title'][idx]
        site = sf['media_name'][idx]
        # downloading article
        print('working on url:', url, '; ', str(idx / len(sf)), ' % done')
        article = newspaper.Article(url)
        try:
            article.download()  # get article
            article.parse()  # parse
            author = article.authors  # get authors
            article = article.text  # get text
            df.loc[len(df)] = [date, url, title, author, site, article]  # load into df
        except Exception as e:
            print("E: " + url)
            df.loc[len(df)] = [date, url, title, '', site, e]
    # write out results i.e "resources/data/kavanaugh_event_articles_method_1.pkl"
    df.to_pickle(save_file)


def clean_html(article):
    """
    method to return article text from html
    :param article: html
    :return:
    """
    try:
        soup = BeautifulSoup(article, 'html.parser')
        art = ''
        article_text = soup.find_all('p')
        # print text
        for paragraph in article_text:
            # get the text only
            text = paragraph.get_text()
            art += " " + text
        art = art.replace('\n', '')
        return art
    except Exception as e:
        print(e)
        return article


def clean_trending_all(article):
    """
    method to clean trending links embedded in big league politcs
    :param article:
    :return:
    """
    embedded_list = re.findall(r'\n\nTrending:(.*?)\n\n', article)
    for e in embedded_list:
        article = article.replace('\n\nTrending:', '',).replace(e, ' ')
    embedded_list = re.findall(r'\n\nRELATED:(.*?)\n\n', article)
    for e in embedded_list:
        article = article.replace('\n\nRELATED:', '', ).replace(e, ' ')
    embedded_list = re.findall(r'\n\nWATCH:(.*?)\n\n', article)
    for e in embedded_list:
        article = article.replace('\n\nWATCH:', '', ).replace(e, ' ')
    return article


def clean_wnd(article):
    """
    method to clean Related columns: & Related stories: at end of wnd articles
    :param article:
    :return:
    """
    try:
        art = article.split("Related columns:\n\n")
        return art[0]
    except Exception as e:
        return article


def clean_wjc(art):
    a = art.replace("We are committed to truth and accuracy in all of our journalism. Read our editorial standards.",
                    "")
    return a


def clean_jpost(art):
    x = "Dear Reader, As you can imagine, more people are reading The Jerusalem Post than ever before. Nevertheless, traditional business models are no longer sustainable and high-quality publications, like ours, are being forced to look for new ways to keep going. Unlike many other news organizations, we have not put up a paywall. We want to keep our journalism open and accessible and be able to keep providing you with news and analysis from the frontlines of Israel, the Middle East and the Jewish World."
    y = "Join Jerusalem Post Premium Plus now for just $5 and upgrade your experience with an ads-free website and exclusive content. Click here"
    a = art.replace(x, "").replace(y, "")
    return a


def clean_wash_times(art):
    x = "Copyright © 2019 The Washington Times, LLC. Click here for reprint permission."
    a = art.replace(x, "")
    return a


def clean_fox_transcript(art):
    x = 'This copy may not be in its final form and may be updated.'
    y = 'Content and Programming Copyright'
    try:
        a = art.split(x)[1].split(y)[0]
        return a
    except Exception as e:
        return art

