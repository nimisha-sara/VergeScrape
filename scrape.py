from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import datetime
import re


class NewsArticle:
    def __init__(self, url: str, author: str, time: str, title: str):
        self.url = url
        self.author = author
        self.time = time
        self.title = title

    def to_dict(self):
        return {
            'url': self.url,
            'headline': self.title,
            'author': self.author,
            'date': self.time
        }


class VergeScrape:
    def __init__(self):
        self.news = []
        self.text_num = {'ONE': 1, 'AN': 1, 'TWO': 2, 'THREE': 3,
                         'FOUR': 4, 'FIVE': 5}
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)

        self.url = "https://www.theverge.com/archives/1"

    def text_to_datetime(self, text_time: str) -> datetime:
        """
        Converts textual time to datetime

        Args:
            text_time (str): A textual time. Eg; 'A MINUTE AGO', '2 HOURS AGO'

        Returns:
            datetime: Returns formatted time
        """
        match = re.match(r'(\w+) (\w+) AGO', text_time)
        if match:
            num_text = match.group(1)
            try:
                num = int(num_text)
            except ValueError:
                num = self.text_num.get(num_text)
            unit = match.group(2)
            now = datetime.datetime.now()
            if unit.startswith('MINUTES'):
                dt = now - datetime.timedelta(minutes=num)
            elif unit.startswith('HOUR'):
                dt = now - datetime.timedelta(hours=num)
            elif unit.startswith('DAY'):
                dt = now - datetime.timedelta(days=num)
            else:
                print(unit)
            text_time = dt.strftime('%b %d %Y %Z') + "GMT" + dt.astimezone().strftime('%z')[:-2] + ":" + dt.astimezone().strftime('%z')[-2:]
        return text_time

    def scrape(self):
        """
        Scrapes news articles from verge.com archives
        """
        self.driver.get(self.url)
        element_type1 = self.driver.find_elements(By.CSS_SELECTOR,
                                                  "div.duet--content-cards--content-card.group")
        element_type2 = self.driver.find_elements(By.CSS_SELECTOR,
                                                  "div.duet--content-cards--content-card.border-solid")
        for div in element_type1:
            article_url = div.find_element(By.CSS_SELECTOR, "h2.font-polysans a").get_attribute("href")
            sub_div = div.find_element(By.CSS_SELECTOR, "div.relative.z-10.inline-block").find_elements(By.TAG_NAME, "div")
            author = " ".join([_div.text for _div in sub_div[0:-1]])
            time = sub_div[-1].text
            title = div.find_element(By.TAG_NAME, "h2").text
            news_article = NewsArticle(article_url, author, self.text_to_datetime(time), title)
            self.news.append(news_article.to_dict())

        for div in element_type2:
            article_url = div.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            title = article_url.split('/')[-1].replace('-', ' ').title()
            text = div.text.split('\n')
            author = text[1]
            time = text[2]
            news_article = NewsArticle(article_url, author, self.text_to_datetime(time), title)
            self.news.append(news_article.to_dict())

    def convert2csv(self) -> str:
        """
        Converts a list of dict to csv

        Returns:
            str: name of csv
        """
        df = pd.DataFrame(self.news)
        _date = str(datetime.datetime.now().strftime('%d%m%y'))
        df.to_csv(f"{_date}.csv", index=False)
        return f"{_date}.csv"
