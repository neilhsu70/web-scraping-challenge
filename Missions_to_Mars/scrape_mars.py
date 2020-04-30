from bs4 import BeautifulSoup
from splinter import Browser
import requests
import pymongo
import pandas as pd
import time 


def scrape():
    mars_news = 'https://mars.nasa.gov/news/'
    mars_image = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    mars_twitter = 'https://twitter.com/marswxreport?lang=en'
    mars_facts = 'https://space-facts.com/mars/'
    mars_hemisphere = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    
    results = {}
    
    # Mars News
    response = requests.get(mars_news)
    time.sleep(3)
    news_pull = BeautifulSoup(response.text, 'lxml')
    title = news_pull.find('div', class_= 'content_title')
    news_title = title.a.text.strip()
    paragraph = news_pull.find('div', class_= 'rollover_description_inner')
    news_paragraph = paragraph.text.strip()
    results['news_title'] = news_title
    results['news_text'] = news_paragraph

    # Mars Image
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(mars_image)
    browser.links.find_by_partial_text('FULL IMAGE').click()
    browser.links.find_by_partial_text('more info').click()
    featured_img_url = browser.find_by_css('.main_image').first['src']
    results['image_url'] = featured_img_url
    browser.quit()

    # Mars Twitter
    response = requests.get(mars_twitter)
    tweet_pull = BeautifulSoup(response.text, 'lxml')
    t = tweet_pull.find_all('p', class_ = 'TweetTextSize TweetTextSize--normal js-tweet-text tweet-text')
    for i in t:
        if 'InSight' in i.text:
            i.a.decompose()
            results['tweet'] = i.text
            break
    
    # Mars Facts
    facts_html = pd.read_html(mars_facts)
    facts_df = facts_html[0]
    facts_df.columns = ['Description', 'Data']
    facts_df.set_index('Description', inplace=True)
    html_table = facts_df.to_html()
    html_table = html_table.replace('\n', '')
    results['table_html'] = html_table

    # Mars Hemispheres
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)
    browser.visit(mars_hemisphere)
    for i in range(4):
        link = browser.links.find_by_partial_text('Hemisphere')[i]
        link.click()
        title = browser.find_by_css('.title').first.text
        url = browser.find_by_text('Sample').first['href']
        results[title] = url
        browser.back()
    browser.quit()
        
    return results
