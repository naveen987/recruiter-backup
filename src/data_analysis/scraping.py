import time
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import random



def pushtoclean():
    """This pushes the resulting dataframe to our cleaning script when called there"""

    driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install()))

    # Number of user listed by overall Reputation pages to scrape. Each page has 36 users.
    # So here 556 pages multiplied by 36 users per page gives 20016 total user profiles
    # Due to testng purposes only 1 page and 5 users are scraped in this script

    num_pages = 150 # increase to add number of pages
    profile_links = []

    for page_number in range(1, num_pages + 1):
        page_url = f"https://stackoverflow.com/users?page={page_number}&tab=reputation&filter=all"
        driver.get(page_url)
        time.sleep(random.randint(7,10)) # Random delay to avoid Rate Limitaion by StackOverflow

        for j in range(1, 6): # here 6 means only 5 users profile links are scraped. This can be increase upto 37.
            try:
                link_element = driver.find_element(By.XPATH, f'/html/body/div[3]/div[2]/div/div[3]/div[1]/div[{j}]/div[2]/a')
                link = link_element.get_attribute('href')
                profile_links.append(link)

            except Exception as e:
                print(f"Error: {e}")

    driver.quit()

    data_list = []

    print('User Profile Links Successfully Scraped!')

    user_counter = 0 # This counter is just to show me how many users have been scraped

    # here I am editing each user profile link to get to their tag link page. Saves a lot of time and clicking for large number of users.
    for profile_url in profile_links:
        user_number = profile_url.split('/')[4]
        username = profile_url.split('/')[5]
        tag_url = f"https://stackoverflow.com/users/{user_number}/{username}?tab=tags"
        try:
            page = requests.get(profile_url)
            page2 = requests.get(tag_url)

            soup = BeautifulSoup(page.text, 'lxml')
            soup2 = BeautifulSoup(page2.text, 'lxml')

            try:
                name_elem = soup.find('div', class_='flex--item mb12 fs-headline2 lh-xs').text.strip()
            except AttributeError:
                name_elem = ''

            try:
                job_title_elem = soup.find('div', class_='mb8 fc-light fs-title lh-xs').text.strip()
            except AttributeError:
                job_title_elem = ''

            try:
                reputation_elem = soup.find_all('div', class_='fs-body3 fc-dark')[0].text
            except IndexError:
                reputation_elem = ''

            try:
                reached_elem = soup.find_all('div', class_='fs-body3 fc-dark')[1].text
            except IndexError:
                reached_elem = ''

            try:
                answers_elem = soup.find_all('div', class_='fs-body3 fc-dark')[2].text
            except IndexError:
                answers_elem = ''

            try:
                questions_elem = soup.find_all('div', class_='fs-body3 fc-dark')[3].text
            except IndexError:
                questions_elem = ''

            try:
                gold_badges_elem = soup.find_all('div', class_='fs-title fw-bold fc-black-800')[0].text.strip()
            except IndexError:
                gold_badges_elem = ''
            try:
                silver_badges_elem  = soup.find_all('div', class_='fs-title fw-bold fc-black-800')[1].text.strip()
            except IndexError:
                silver_badges_elem = ''
            try:
                bronze_badges_elem = soup.find_all('div', class_='fs-title fw-bold fc-black-800')[2].text.strip()
            except IndexError:
                bronze_badges_elem = ''

            try:
                numberoftags = soup2.find('h2', class_='flex--item fs-title mb0').text.strip()
            except AttributeError:
                numberoftags = ''

            try:
                tags = soup2.find('div', class_='ba bc-black-100 bar-md').text.strip()
                cleaned_tags = ' '.join(tags.split())
                user_tags = cleaned_tags.split()
                user_tags_str = ' '.join(user_tags)
            except AttributeError:
                user_tags_str = ''

            try:
                join_date_raw = soup.find('ul',class_='list-reset s-anchors s-anchors__inherit d-flex fc-light gs8 mln4 fw-wrap').text.strip()
                last_seen_index = join_date_raw.find("Last seen")
                join_date = join_date_raw[:last_seen_index].strip()
            except AttributeError:
                join_date = ''

            data = {
                'Name': name_elem,
                'Membership Period': join_date,
                'Job Title': job_title_elem,
                'Reputation': reputation_elem,
                'Reached': reached_elem,
                'Answers': answers_elem,
                'Questions': questions_elem,
                'Gold Badges': gold_badges_elem,
                'Silver Badges': silver_badges_elem,
                'Bronze Badges': bronze_badges_elem,
                'Number of Tags': numberoftags,
                'User Tags': user_tags_str,
            }

            data_list.append(data)
            user_counter += 1  # Increment the counter
            print(f"\r{user_counter} User{'s' if user_counter > 1 else ''} Data Scraped", end='', flush=True)
            time.sleep(random.randint(7, 9)) # another delay before scraping next user


        except Exception as e:
            print(f"An error occurred: {e}")

    df = pd.DataFrame(data_list)
    return df  #returns this raw data to the cleaning script
