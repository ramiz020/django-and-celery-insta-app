from celery import shared_task
from .models import Instagram,Profiles
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import time
import logging

from celery.decorators import periodic_task
from celery.task.schedules import crontab
from insta.celery import app

logger = logging.getLogger(__name__)

@app.task
def add_user(username,password):
    while True:
        try:
    # Set up the web driver for Chrome.
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get('https://www.instagram.com/')

            # Wait for the page to load.
            time.sleep(2)

            # Log in.
            driver.find_element(By.NAME,'username').send_keys(username)
            driver.find_element(By.NAME,'password').send_keys(password)
            driver.find_element(By.CSS_SELECTOR,'button[type=submit]').click()

            # Wait for the page to load.
            time.sleep(3)

            # Navigate to the target profile's page.
            driver.get('https://www.instagram.com/' + username)

            # Wait for the page to load.
            time.sleep(2)

            # Get the follower count.
            followers_element = driver.find_element(By.XPATH,'//a[contains(@href, "/followers")]/span')
            followers_count = followers_element.get_attribute('title').replace(',', '')

            # Get the following count.
            following_element = driver.find_element(By.XPATH,'//a[contains(@href, "/following")]/span')
            following_count = following_element.text.replace(',', '')
            insta = Instagram.objects.get_or_create(username = username, following = following_count, followers = followers_count)
            profile = Profiles.objects.get_or_create(username = username, password = password)
            # Quit the driver.  
            break
        except Exception as e:
            print("An error occurred:", e) 
        finally:
            driver.quit()

@app.task
def check():
    try:
        profiles = Profiles.objects.all()

        # Change the following variables to match your login information and the target profile's username.
        for i in profiles:
            username = i.username
            password = i.password

            # Set up the web driver for Chrome.
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(chrome_options=chrome_options)
            driver.get('https://www.instagram.com/')

            # Wait for the page to load.
            time.sleep(2)

            # Log in.
            driver.find_element(By.NAME,'username').send_keys(username)
            driver.find_element(By.NAME,'password').send_keys(password)
            driver.find_element(By.CSS_SELECTOR,'button[type=submit]').click()

            # Wait for the page to load.
            time.sleep(3)

            # Navigate to the target profile's page.
            driver.get('https://www.instagram.com/' + username)

            # Wait for the page to load.
            time.sleep(2)

            # Get the follower count.
            followers_element = driver.find_element(By.XPATH,'//a[contains(@href, "/followers")]/span')
            followers_count = followers_element.get_attribute('title').replace(',', '')

            # Get the following count.
            following_element = driver.find_element(By.XPATH,'//a[contains(@href, "/following")]/span')
            following_count = following_element.text.replace(',', '')


            # Uptade database
            insta = Instagram.objects.filter(username=username).update(username = username, following = following_count, followers = followers_count)
    except Exception as e:
        print("An error occurred:", e)

    finally:
        driver.quit()


@periodic_task(run_every=(crontab(minute='*/10')))
def run_task():
    check.delay()