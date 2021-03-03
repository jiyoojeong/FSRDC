# TODO SCOPUS
from pyscopus import Scopus
from pybliometrics.scopus import ScopusSearch
import pandas as pd
import requests
import json


# use Pyscopus http://zhiyzuo.github.io/python-scopus/
# json and requests https://kitchingroup.cheme.cmu.edu/blog/2015/04/03/Getting-data-from-the-Scopus-API/
# PILIOMETRICS (seems most reasonable to use: https://pybliometrics.readthedocs.io/en/stable/examples/AbstractRetrieval.html

'''NOTE: 
The API database includes thing that are published after 1995, and it may not be updated as quickly as the web database. 
For example the web page reports 7that are published after 1995, and it may not be updated as quickly as the web database. 
For example the web page reports 799 documents and 3143 citations. 
In the next sections we will use the search API, which returns the same information 
as what is on the web.'''


# APIKEY = '79424cec4d82340623ef2aa8532c20b9'

def dodis():
    final_search = pd.read_csv('input_data/to_find_final_2.csv', header=0, )
    key = '79424cec4d82340623ef2aa8532c20b9'
    scopus = Scopus(key)
    for idx, row in final_search.iterrows():
        title = row['title_original']
        stripped_title = row['Title']
        aid = row['articleID']

        search = scopus.search("KEY(interdisciplinary collaboration)", count=20)
        print(search)
        break
        #scopus_id = search['scopus_id']
        #pub_info = scopus.retrieve_abstract(scopus_id)
        #pub_info['abstract']


def dodis2():
    final_search = pd.read_csv('input_data/to_find_final_2.csv', header=0, )
    key = '79424cec4d82340623ef2aa8532c20b9'
    s = ScopusSearch('FIRSTAUTH ( kitchin  j.r. )')
    print(s)

    '''
    resp = requests.get(
        "http://api.elsevier.com/content/search/scopus?query=TITLE()&field=dc:identifier&count=100",
        headers={'Accept': 'application/json',
                 'X-ELS-APIKey': MY_API_KEY})

    results = resp.json()

    return [[str(r['dc:identifier'])] for r in results['search-results']["entry"]]
    '''


if __name__ == '__main__':
    dodis2()
