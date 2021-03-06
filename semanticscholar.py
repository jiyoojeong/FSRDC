'''
http://s2-public-api-prod.us-west-2.elasticbeanstalk.com/

The API is freely available, but enforces a rate limit and will respond with HTTP status 429 'Too Many Requests' if the limit is exceeded (100 requests per 5 minute window per IP address). Higher rates of access are allowed to Data Partners of Semantic Scholar - interested parties should submit a request via the partnership contact form to determine if a private API key is appropriate for your request.
'''

# use crossref.org metadata to get the DOI of each article
# use DOI to search via semantic scholar

# webdriver imports
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fuzzywuzzy import fuzz

# basic other imports
import nltk
import os
import re
import time
import numpy as np
import pandas as pd


def semanticsDOI():

    final_search = pd.read_csv('output_data/abstracts_v1.csv', header=0, )

    ### Chrome Options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # LIKELY NOT NEEDED
    prefs = {"download.default_directory": "/Users/jiyoojeong/desktop/c/FSRDC_Papers/output_data/DOI"}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(executable_path='/Users/jiyoojeong/desktop/c/FSRDC_Papers/chromedriver88',
                              options=chrome_options)

    url = 'https://www.semanticscholar.org/search'
    if 'abstract' not in final_search.columns:
        final_search['abstract'] = 1
    print("total papers: ", len(final_search))
    print('final search ||||\n', final_search)
    for idx, paper in final_search.iterrows():
        aid = paper['articleID']
        year = paper['year']
        title = paper['Title']
        journal = paper['journal']
        a = paper['abstract']

        print('=============journal no.', str(idx + 1), '\n:::', aid, ':::', title)
        print('abs', a, type(a))
        if a != None and a != np.nan and a != 0 and a != '0': #and a != 'No Result.'
            #print('no res', a == 'No Result.')
            #print('nan', a == np.nan)
            #print('None', a == None)
            #print('0', a == 0)
            #print('string 0', a == '0')
            assert len(a) >= 3
            print("this is alr done")
            # print(a)
        else:
            driver.get(url)
            search_bar = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-form"]/div/div/input')))
            time.sleep(np.random.uniform(1, 2))
            query = title + ' ' + str(year)
            search_bar.send_keys(query)
            time.sleep(np.random.uniform(1, 2))
            driver.find_element_by_xpath('//*[@id="search-form"]/div/div/button').click()
            time.sleep(np.random.uniform(1, 2))
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div[1]/div[2]/div/div[1]/div/div[1]/div')))
            except:
                try:
                    driver.refresh()
                    search_bar = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="search-form"]/div/div/input')))
                    time.sleep(np.random.uniform(1, 2))
                    search_bar.send_keys(query)
                    time.sleep(np.random.uniform(1, 2))
                    driver.find_element_by_xpath('//*[@id="search-form"]/div/div/button').click()
                    time.sleep(np.random.uniform(1, 2))
                except:
                    driver.quit()
                    driver = webdriver.Chrome(executable_path='/Users/jiyoojeong/desktop/c/FSRDC_Papers/chromedriver88',
                                              options=chrome_options)
                    driver.get(url)
                    search_bar = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="search-form"]/div/div/input')))
                    time.sleep(np.random.uniform(1, 2))
                    search_bar.send_keys(query)
                    time.sleep(np.random.uniform(1, 2))
                    driver.find_element_by_xpath('//*[@id="search-form"]/div/div/button').click()
                    time.sleep(np.random.uniform(1, 2))
            result_titles = driver.find_elements_by_xpath('//*[@id="main-content"]/div[1]/div/div[1]/a/div')
            # ONLY LOOK AT FIRST PAGE OF SEARCH RESULTS.
            if len(result_titles) == 0:
                print("NO RESULTS FOUND FOR \'", title, "\'")
                final_search.loc[idx, 'abstract'] = 'No Result.'

            for res in result_titles:
                noabs = True
                # check that title is correct
                abstract = ''
                print("restitle:", res.text)
                if noabs:
                    rtitle = res.text
                    rtitle = rtitle.lower()
                    # diffscore = nltk.edit_distance(rtitle, title)/len(title)
                    simscore = fuzz.partial_ratio(rtitle, title)

                    if simscore < .5:
                        print('ISS TOO DIFF!')
                        print(rtitle, title, simscore)
                        final_search.loc[idx, 'abstract'] = 'Titles are different. Check for longer names.'
                    else:
                        if len(result_titles) > 1:
                            ichild = '[' + str(idx + 1) + ']'
                        else:
                            ichild = ''

                        tldr_abs = '//*[@id="main-content"]/div[1]/div/div' + ichild + '/div[1]/div/span[3]'
                        full_abs = '//*[@id="main-content"]/div[1]/div/div' + ichild + '/div[1]/span'

                        tldrexp = '//*[@id="main-content"]/div[1]/div/div' + ichild + '/div[1]/div/span[last()]'
                        fullexp = '//*[@id="main-content"]/div[1]/div/div' + ichild + '/div[1]/span/span[last()]'

                        try:
                            driver.find_element_by_xpath(fullexp).click()
                            print("EXPANDED REG.")
                            abstract = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, full_abs))).text
                            noabs = False
                            final_search.loc[idx, 'abstract'] = abstract
                        except:
                            # TRYING TLDR EXPANSION.
                            try:
                                driver.find_element_by_xpath(tldrexp).click()
                                print("EXPANDED TLDR.")
                                abstract = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, tldr_abs))).text
                                noabs = False
                                final_search.loc[idx, 'abstract'] = abstract
                            except:
                                print("SOMETHING WENT WRONG WITH EXPAND... NO RES?")
                                whole_res = driver.find_element_by_xpath('//*[@id="main-content"]/div[1]/div/div'+ichild).text
                                missed = 'ABSTRACT' in whole_res or 'Expand' in whole_res
                                if missed:
                                    print('wrong query results ----------')
                                    print(whole_res)
                                    print('-------------------------------')
                                final_search.loc[idx, 'abstract'] = 'ERR'

                if abstract:
                    print('----------ABS::', abstract)
                else:
                    print('no abstract found.')

                print('paper::', final_search.loc[idx, :])

        final_search.to_csv('output_data/abstracts_v1.csv', index=False)
        final_search = pd.read_csv('output_data/abstracts_v1.csv', header=0)
    return final_search


def resetfile():
    final_search = pd.read_csv('input_data/to_find_final_3.csv', header=0, )
    print('fin done')
    abstracts = pd.read_csv('output_data/abstracts_v1.csv', header=0)
    print('abs done')
    print(abstracts.head())
    final_search['abstract'] = 0
    for idx, row in abstracts.iterrows():
        aid = row['articleID']
        a = row['abstract']
        fidx = final_search['articleID'] == aid
        # print('fidx')
        if a == 0:
            final_search.loc[fidx, 'abstract'] = 0
        elif a != 0:
            final_search.loc[fidx, 'abstract'] = a
        else:
            final_search.loc[fidx, 'abstract'] = 0

    final_search.to_csv('output_data/abstracts_v1.csv', index=False)


if __name__ == '__main__':
    # reset
    # resetfile()
    fin = semanticsDOI()
    fin.to_csv('output_data/sus.csv', index=False)

