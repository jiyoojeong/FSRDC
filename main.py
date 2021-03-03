# coding=utf-8
# This is a sample Python script.

# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from wos import WosClient
import wos.utils
import pandas as pd
from selenium import webdriver
import time
import numpy as np
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import nltk
import os
import re


def scrape():
    ### Chrome Options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-dev-shm-usage')

    prefs = {"download.default_directory": "/Users/jiyoojeong/desktop/c/FSRDC_Papers/output_data/raw"}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(executable_path='/Users/jiyoojeong/desktop/c/FSRDC_Papers/chromedriver88',
                              options=chrome_options)

    url = 'http://apps.webofknowledge.com.libproxy.berkeley.edu/WOS_GeneralSearch_input.do?product=WOS&search_mode=GeneralSearch&SID=8CA4Lfkd4jljZCTArfL&preferencesSaved='
    driver.get(url)

    # click and logins
    time.sleep(np.random.uniform(1, 2))
    driver.find_element_by_xpath('//*[@id="calnet_link"]').click()
    time.sleep(np.random.uniform(2, 3))

    username = driver.find_element_by_xpath('//*[@id="username"]')
    username.send_keys('jiyoojeong')  # ENCRYPT IF NEEDED
    time.sleep(np.random.uniform(1, 2))
    pw = driver.find_element_by_xpath('//*[@id="password"]')
    pw.send_keys('Poobearluv.12')  # ENCRYPT IF NEEDED
    time.sleep(np.random.uniform(1, 2))
    driver.find_element_by_xpath('//*[@id="submit"]').click()
    time.sleep(np.random.uniform(2, 3))

    try:
        driver.find_element_by_xpath('//*[@id="value(input1)"]')
    except:
        # webdriverwait
        try:
            loading = WebDriverWait(driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="value(input1)"]')))
        except TimeoutException:
            print("WOS page did not load.")
            driver.quit()
            exit()

    bare_details = pd.read_csv('input_data/fsrdc_papers_bare_details_2.csv', header=0, error_bad_lines=False)
    # segmnt = bare_details[['article_id', 'title']]
    citations = []
    citation_lengths = []
    use_journal = False
    try:
        spelling_checks = pd.read_csv('input_data/spellingchecks.csv', header=0)
    except:
        spelling_checks = pd.DataFrame(columns=['aid', 'title'])

    try:
        nocits = pd.read_csv('input_data/no_citations.csv', header=0)
    except:
        nocits = pd.DataFrame(columns=['aid', 'title'])

    for idx, row in bare_details.iterrows():
        aid = row['article_id']
        title = row['title']

        if re.search(r'\bor\b', title):
            title = re.sub(r'\bor\b', ' ', title)
            #print('quotes changed==', title)

        if re.search(r'\band\b', title):
            title = re.sub(r'\band\b', ' ', title)
            #print('and changed==', title)

        if re.search(r'\"', title):
            title = re.sub(r'\"', '', title)
            #print('and changed==', title)

        if re.search(r'\"{2,}', title):
            title = re.sub(r'\"{2,}', '\"', title)
            #print('quotes changed==', title)

        if re.search(r'\bstartup\b', title):
            title = re.sub(r'\bstartup\b', '(startup or start up)', title)
            #print('quotes changed==', title)
        if re.search(r'\bstartups\b', title):
            title = re.sub(r'\bstartups\b', '(startups or start ups)', title)

        if re.search(r'\bmicro\b', title):
            title = re.sub(r'\bmicro\b', 'micro ', title)

        if re.search(r'\bus\b', title):
            # print('helo - replacing \'us\'...')
            title = re.sub(r'\bus\b', '', title)

        if re.search(r'\busa\b', title):
            # print('helo - replacing \'us\'...')
            title = re.sub(r'\busa\b', '', title)

        if re.search(r'\bu\$s\b', title):
            # print('helo - replacing \'us\'...')
            title = re.sub(r'\bu\$s\b', '', title)
            # print('us changed==', title)

        if re.search(r'\br&d\b', title):
            title = re.sub(r'\br&d\b', 'r d', title)
                # print('us changed==', title)
            #print('quotes changed==', title)
        if re.search(r'--', title):
            title = re.sub(r'--', ' or ', title)
                # print('us changed==', title)
            #print('quotes changed==', title)

        if re.search(r'nonlinear', title):
            title = re.sub(r'nonlinear', 'non linear', title)
                # print('us changed==', title)
            #print('quotes changed==', title)

        if re.search(r'wellbeing', title):
            title = re.sub(r'wellbeing', 'well being', title)
                # print('us changed==', title)
            #print('quotes changed==', title)

        if re.search(r'\bwhats\b', title):
            title = re.sub(r'\bwhats\b', 'what s', title)
                # print('us changed==', title)
            #print('quotes changed==', title)

        if re.search(r'\bnot\b', title):
            title = re.sub(r'\bnot\b', '\"not\"', title)
                # print('us changed==', title)
            #print('quotes changed==', title)

        if re.search('ethnicity language and workplace segregation evidence from a new matched employer employee data set', title):
            newstr = 'Workplace segregation in the United States: Race ethnicity skill'
            title = newstr #re.sub('ethnicity language and workplace segregation evidence from a new matched employer employee data set', newstr, title)

        journal = row['journal']
        year = row['year']
        if 'output_data/raw' not in os.getcwd():
            os.chdir('output_data/raw')
        if str(aid) + '.txt' in os.listdir():
            print('this is already downloaded.')
        elif idx < 0 or aid in nocits['aid']:
            print('this has already been looked up. skipping.')
        else:
            search_bar = WebDriverWait(driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="value(input1)"]')))

            print('#', str(idx+1), ':::articleid:', str(aid), '\n:::title:', title)
            citation_elements = []
            '''
            try:
                print('selecting db...')
                select = Select(driver.find_element_by_id("databases"))
                # databases selector xpath: '//*[@id="databases"]'
                #print([s.text for s in select.options])
                driver.find_element_by_xpath('//*[@id="select.database.stripe"]/div/div/span[2]/span[1]/span/span[2]').click()

                #exit()

                #driver.find_element_by_xpath('//*[@id="databases"]').click()
                #time.sleep(.5)
                #print('trying to open...')

                print('=>select opened?')
                #select.select_by_index(1)
                time.sleep(1)
                #
                #select.select_by_value('All Databases')
                select.select_by_visible_text('All Databases')
                print('=>selected all db')
            except:
                print("=>ERR IN SETTING DB.")
            '''

            try:
                # send keys
                search_bar.clear()
                search_bar.send_keys(title)
                category_bar = driver.find_element_by_xpath('//*[@id="select1"]')

                # select title
                select = Select(driver.find_element_by_id('select1'))
                select.select_by_visible_text('Title')
                if use_journal:
                    try:
                        driver.find_element_by_xpath('//*[@id="addSearchRow1"]/a').click()
                        search_bar2 = driver.find_element_by_xpath('//*[@id="value(input2)"]')
                        search_bar2.clear()
                        search_bar2.send_keys(journal)
                        # select title
                    except:
                        # do nothing
                        search_bar2 = driver.find_element_by_xpath('//*[@id="value(input2)"]')
                        search_bar2.clear()
                        search_bar2.send_keys(journal)
                        # select title

                    try:
                        print('keys sent with pub name.')
                        select = Select(driver.find_element_by_id('select2'))  # TODO: maybe select2?
                        select.select_by_visible_text('Publication Name')
                    except:
                        # do nothing
                        print('keys sent without pub name.')

                        # TODO: check for 'no result' case, and for some it comes up as "cannot do this"
                    time.sleep(np.random.uniform(1, 2))
                    print('sending.')
                    driver.find_element_by_xpath('//*[@id="searchCell2"]/span[1]/button').click()  # send keys
                    #time.sleep(np.random.uniform(4, 6))
                else:
                    driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button').click()
                    #time.sleep(np.random.uniform(4, 6))
                    print('sending.')
                time.sleep(np.random.uniform(2, 3))
                try:
                    spelling = True
                    try:
                        restest = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[contains(@id,"RECORD_1")]/div[3]/div/div[1]/div/a/value')))
                    except:
                        print('no load...')
                        spelling_checks = spelling_checks.append({'aid': aid, 'title': title}, ignore_index=True)
                        print(spelling_checks.shape)
                        spelling = False

                    if spelling:
                        next_page = driver.find_element_by_xpath(
                            '//*[@id="summary_navigation"]/nav/table/tbody/tr/td[3]/a').get_attribute('href')
                        print('getting res.')
                        results = driver.find_elements_by_xpath('//*[contains(@id,"RECORD_")]/div[3]/div/div[1]/div/a/value')
                        # = driver.find_element_by_xpath('//*[contains(@id,"show_journal_overlay_link")]/a/span/value')
                        '//*[contains(@id,"show_journal_overlay_link")]/a/span/value'

                        citations_temp = driver.find_elements_by_xpath('//*[contains(@id,"RECORD_")]/div[4]/div[1]')
                        keep_idx = []
                        print('len', len(results))

                        # '//*[@id="RECORD_1"]/div[3]/div/div[1]/div/a/value'
                        # '//*[@id="RECORD_2"]/div[3]/div/div[1]/div/a/value'

                        for i in range(0, len(results)):
                            #print('-----------------A------------------')
                            res_text = results[i].text
                            # print(res_text)
                            #print('-----------------B------------------')
                            score = nltk.edit_distance(res_text.lower(), title) / len(title)

                            #print('-----------------C------------------')
                            if score > .3 and i >= 1:
                             #   print('-----------------D------------------')
                                print(title, 'to', res_text, 'is too diff. Remove.', 'score:', score)
                                # remove from list
                            else:
                              #  print('-----------------E------------------')
                                keep_idx.append(i)


                        results = filter(results, keep_idx)
                        # journals = filter(journals, keep_idx)
                        citations_temp = filter(citations_temp, keep_idx)
                        print('finished filter stage')

                        # click and download!!
                        for citation in citations_temp:
                            print("clicking stage.")
                            try:
                                url = citation.find_element_by_tag_name('a').get_attribute('href')
                                print(' -- url gotten.')
                                driver.get(url)
                                time.sleep(3)
                                driver.find_element_by_xpath(
                                    '//*[@id="view_citation_report_image_placeholder"]/div/div/a').click()
                                time.sleep(np.random.uniform(1, 2))

                                driver.find_element_by_xpath(
                                    '//*[@id="cr-export-options"]/div/span/span/span[1]/span/span[2]/b').click()
                                time.sleep(np.random.uniform(1, 2))
                                # select txt file
                                select = Select(driver.find_element_by_id('cr_saveToMenuTop'))
                                # '//*[@id="cr_saveToMenuTop"]'

                                select.select_by_visible_text('Save to Text File')
                                print('select works')
                                time.sleep(np.random.uniform(1, 2))
                                # time.sleep(30)

                                # not necessary
                                # driver.find_element_by_xpath('//*[@id="cr-export-options"]/div/span/span/span[1]').click()

                                print('downloading...')
                                all_records = WebDriverWait(driver, 100).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="numberOfRecordsAllOnPage"]')))
                                all_records.click()

                                export = WebDriverWait(driver, 100).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="exportButton"]')))
                                export.click()

                                time.sleep(np.random.uniform(7, 10))

                                try:
                                    # rename file
                                    # print(os.getcwd())
                                    if os.getcwd() != '/Users/jiyoojeong/Desktop/C/FSRDC_Papers/output_data/raw':
                                        os.chdir('output_data/raw')
                                    print(os.getcwd())
                                    # print(type(aid), aid)
                                    said = str(aid)
                                    if said + '.txt' in os.listdir():
                                        print("this article file already exists...")
                                    try:
                                        os.rename('savedrecs.txt', said + '.txt')
                                    except:
                                        print('doing some weird shit')
                                        lst = os.listdir()
                                        print(lst)
                                        mask = [1 if 'savedrecs' in n else 0 for n in lst]
                                        i = np.argmax(mask)[0]
                                        print(lst[i])
                                        os.rename(lst[i], aid + '.txt')
                                    print('this worked.')
                                except OSError:
                                    # Failed
                                    print("FAILED TO change name.")
                                driver.back()
                                time.sleep(np.random.uniform(1, 2))
                                # driver.back() #TODO: is this needed?

                                citation_elements += citations_temp
                                citations_temp = []
                            except:
                                nocits = nocits.append({'aid': aid, 'title': title}, ignore_index=True)
                                print("this paper was not cited ever.")


                        ## LOOP FOR ADDITIONAL PAGES
                        while next_page != "javascript: void('paginationNext')":

                            print('getting more results.')
                            keep_idx = []

                            next_page = driver.find_element_by_xpath(
                                '//*[@id="summary_navigation"]/nav/table/tbody/tr/td[3]/a').click()
                            time.sleep(np.random.uniform(.5, 1))

                            results = driver.find_elements_by_xpath('//*[@id="RECORD_"]/div[3]/div/div[1]/div/a/value')
                            journals = driver.find_element_by_xpath(
                                '//*[contains(@id,"show_journal_overlay_link")]/a/span/value')

                            citations_temp += driver.find_elements_by_xpath('//*[contains(@id,"RECORD_")]/div[4]/div[1]')

                            for i in range(0, len(results)):
                                res_text = results[i].text
                                score = nltk.edit_distance(res_text.lower(), title) / len(title)
                                if score > .3 and i > 1:
                                    print(title, 'to', res_text, 'titles too different.')
                                    # remove from list
                                    #if len(results) <= 1:
                                        #print('few results, better check journals')
                                        #resjournal = journals[i].text
                                        #jscore = nltk.edit_distance(resjournal.lower(), journal)
                                        #print('jscore gotted.')
                                        #if resjournal in journal or journal in resjournal:
                                        #    print(resjournal, '==', journal, '=BY=', jscore)
                                            # do not remove.
                                            # keep_idx.append(i)
                                else:
                                    keep_idx.append(i)

                            results = filter(results, keep_idx)
                            citations_temp = filter(citations_temp, keep_idx)
                            print('filtered, len_citations temp=', len(citations_temp))

                            for citation in citations_temp:
                                #print("clicking stage.")
                                url = citation.find_element_by_tag_name('a').get_attribute('href')
                                #print(' -- url gotten.')
                                driver.get(url)
                                time.sleep(1)
                                driver.find_element_by_xpath(
                                    '//*[@id="view_citation_report_image_placeholder"]/div/div/a').click()
                                time.sleep(np.random.uniform(1, 2))

                                driver.find_element_by_xpath(
                                    '//*[@id="cr-export-options"]/div/span/span/span[1]/span/span[2]/b').click()
                                time.sleep(np.random.uniform(1, 2))
                                # select txt file
                                select = Select(driver.find_element_by_id('cr_saveToMenuTop'))
                                # '//*[@id="cr_saveToMenuTop"]'

                                select.select_by_visible_text('Save to Text File')
                                print('select works')
                                time.sleep(np.random.uniform(1, 2))
                                # time.sleep(30)

                                # not necessary
                                # driver.find_element_by_xpath('//*[@id="cr-export-options"]/div/span/span/span[1]').click()

                                print('input found.')
                                all_records = WebDriverWait(driver, 100).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="numberOfRecordsAllOnPage"]')))
                                all_records.click()

                                export = WebDriverWait(driver, 100).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="exportButton"]')))
                                export.click()

                                # wait for download
                                wait_time = download_wait('output_data/raw', 30)
                                if wait_time == 30:
                                    download_wait('output_data/raw', 30)

                                print('this worked.')
                                try:
                                    # rename file
                                    os.chdir('output_data/raw')
                                    if aid + '.txt' in os.listdir():
                                        print("this article file already exists... something went wrong.")
                                    os.rename('savedrecs.txt', aid + '.txt')
                                except OSError:
                                    # Failed
                                    print("FAILED TO change name.")
                            next_page.click()

                            citation_elements += citations_temp
                            citations_temp = driver.find_elements_by_xpath('//*[contains(@id,"RECORD_")]/div[4]/div[1]')
                            time.sleep(np.random.uniform(.5, 1))
                        print('len citations == ', len(citation_elements))

                        # aggregate
                        citation_lengths.append(len(citation_elements))
                        citations.append(citation_elements)
                except:
                    citation_lengths.append(0)
                    citations.append([])
                    print('Some error occured...')

                # return to main search
                driver.find_element_by_xpath('/html/body/div[1]/h1/div/a').click()
                print('returning...')
                time.sleep(np.random.uniform(3, 4))

            except BaseException:
                print("cannot do this :(")
                driver.quit()

    try:
        spelling_checks.drop_duplicates(inplace=True)
        spelling_checks.to_csv('../../input_data/spellingchecks.csv', index=False)
        print('--- saved spellings ---')
    except:
        print('could not save spelling checks. Printing out instead.')
        print('====================SPELLINGS?')
        print(spelling_checks)
        # with WosClient('jiyooj@gmail.com', 'Poobearluv.1!') as client:
        #    print(wos.utils.query(client, 'TI=' + title))

    try:
        nocits = nocits.drop_duplicates(inplace=True)
        nocits.to_csv('../../input_data/no_citations.csv', index=False)
        print('--- saved nocits ---')
    except:
        print('could not saveno citations. Printing out instead.')
        print('====================NOCITS?')
        print(nocits)
        # with WosClient('jiyooj@gmail.com', 'Poobearluv.1!') as client:
        #    print(wos.utils.query(client, 'TI=' + title))


def download_wait(directory, timeout, nfiles=None):
    """
    Wait for downloads to finish with a specified timeout.

    Args
    ----
    directory : str
        The path to the folder where the files will be downloaded.
    timeout : int
        How many seconds to wait until timing out.
    nfiles : int, defaults to None
        If provided, also wait for the expected number of files.

    """
    seconds = 0
    dl_wait = True
    while dl_wait and seconds < timeout:
        time.sleep(1)
        dl_wait = False
        files = os.listdir(directory)
        if nfiles and len(files) != nfiles:
            dl_wait = True

        for fname in files:
            if fname.endswith('.crdownload'):
                dl_wait = True

        seconds += 1
    return seconds


def filter(lst, idx):
    return [lst[i] for i in idx]


if __name__ == '__main__':
    scrape()
    #os.chdir('output_data/raw')
    num = len(os.listdir())
    print("total files:", str(num))


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
