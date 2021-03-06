import os
import pandas as pd
import re
import numpy as np

def extract():
    failed = []
    cols = ["Title", "Authors", "Corporate Authors", "Editors", "Book Editors", "Source Title", "Publication Date",
     "Publication Year", "Volume", "Issue", "Part Number", "Supplement", "Special Issue", "Beginning Page",
     "Ending Page", "Article Number", "DOI", "Conference Title", "Conference Date", "Total Citations",
     "Average per Year", "1900", "1901", "1902", "1903", "1904", "1905", "1906", "1907", "1908", "1909", "1910", "1911",
     "1912", "1913", "1914", "1915", "1916", "1917", "1918", "1919", "1920", "1921", "1922", "1923", "1924", "1925",
     "1926", "1927", "1928", "1929", "1930", "1931", "1932", "1933", "1934", "1935", "1936", "1937", "1938", "1939",
     "1940", "1941", "1942", "1943", "1944", "1945", "1946", "1947", "1948", "1949", "1950", "1951", "1952", "1953",
     "1954", "1955", "1956", "1957", "1958", "1959", "1960", "1961", "1962", "1963", "1964", "1965", "1966", "1967",
     "1968", "1969", "1970", "1971", "1972", "1973", "1974", "1975", "1976", "1977", "1978", "1979", "1980", "1981",
     "1982", "1983", "1984", "1985", "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995",
     "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009",
     "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "sourcearticleID"]

    df = pd.DataFrame(columns=cols)
    try:
        os.chdir('output_data/raw')
    except:
        print('os already in raw dir.')

    i = 1
    for fname in os.listdir():
        if '.txt' in fname:
            aid = re.sub('.txt', '', fname)
            print('=aid', i, '=', aid, fname)
            i += 1


            try:
                bb = pd.read_csv(fname, header=2)
                bb['sourcearticleID'] = aid
                print(bb.head())
                df = df.append(bb, ignore_index=True, sort=False)
            except:
                f = open(fname, "r")
                tf = []
                for line in f:
                    vals = line.split(',')
                    tf.append((len(vals) >= len(cols)-1, len(vals)))
                print(tf)
                failed.append(fname)

            #print(df)
            #break
    return df, failed


def twotocsv():
    if 'raw' in os.getcwd():
        os.chdir('..')
    elif 'output_data' not in os.getcwd():
        os.chdir('output_data')

    print(os.getcwd())
    nlsy = pd.read_csv('NLSY.txt', sep='\n', header=None)
    psid = pd.read_csv('PSID.txt', sep='\n', header=18).values.reshape(-1, 2)
    psid = pd.DataFrame(psid, columns=['info', 'keywords'])

    # SPLIT PSID
    psid['split'] = psid['info'].str.split('  ')
    #print(psid.columns)

    #print(pd.DataFrame(psid['split']))
    #print(psid.columns)
    pcols1 = ['authors', 'info2']

    psid[pcols1] = pd.DataFrame(pd.DataFrame(psid['split']).split.tolist(), columns=pcols1, index=psid.index)
    psid['info2 split'] = psid['info2'].str.rsplit(r".", n=4)
    #print(psid.columns)
    #print(psid['info2 split'].tolist())
    #print(psid['info2 split'].value_counts())
    psidsub = [p[0:3] for p in psid['info2 split']]
    for i, p in enumerate(psid['info2 split']):
        try:
            title = p[0]
            journal = p[1]
            year = p[2]

            if '?' in title and len(journal) == 5:
                #print( title,'--', journal,'--', year)
                titleold = title
                title = re.sub(r'\?[a-zA-Z0-9\s]*', '?', titleold)
                year = journal
                journal = re.sub(r'^[a-zA-Z0-9\s]*\?', '', titleold)
                #print('CHANGED', title,'--', journal,'--', year)

            if '?' in title and (len(p) == 3 or 'Forthcoming' in p):

                print( title,'--', journal,'--', year)
                titleold = title
                title = re.sub(r'\?[a-zA-Z0-9\s]*', '?', titleold)
                year = journal
                journal = re.sub(r'^[a-zA-Z0-9\s]*\?', '', titleold)
                print('CHANGED', title,'--', journal,'--', year)

            psid.loc[i, 'title'] = title
            psid.loc[i, 'journal'] = journal
            psid.loc[i, 'year'] = year
        except:
            print(i, p)
            print(psid.loc[i, 'split'])
            print(psid.loc[i, 'info2'])
            print(psid.loc[i, 'blank1'])
            break

    #print(psidsub)

    '''print('00000')
    filter = [True if len(s) != 5 else False for s in psid['info2 split'].tolist()]
    print(sum(filter), 'out of ', len(filter))
    print(filter)
    print(psid.loc[np.argmax(filter), 'info2 split'])
    #print(psid.loc[filter, 'info2 split'])
    # print('----', psid['info2 split'].tolist())
    print('00000')
    print(psid3)'''
    #print("---------")
    #print(psid.loc[psid['year'].str.len() > 4, :])

    pcols = ['title', 'journal', 'year']
    # psid[pcols] = pd.DataFrame(pd.DataFrame(psid['info2'].str.split('.')).tolist())

    psidfin = psid[['title', 'keywords', 'authors', 'journal', 'year']]
    print(psidfin.columns)
    # print(psidfin)
    # print(psid['b1'].value_counts())
    #print(psid['year'].value_counts())
    #psid2 = psid[['title','journal','authors','year','keywords']]

    count = 0
    for i, row in psidfin.iterrows():
        y = row['year']
        if len(y) > 5 and 'Forthcoming' not in y:
            count += 1
            print('==============')
            print(psid.loc[i, 'info2 split'])
            # print(len(psid.loc[i, 'info2 split']))
            if len(psid.loc[i, 'info2 split']) == 5:
                info2 = psid.loc[i, 'info2 split']
                s2 = '.'.join(info2)
                print(s2)
                if 'U.S.' in s2:
                    s3 = re.sub(r'U\.S\.*', 'U S', s2)
                    s2 = s3
                if 'U. S.' in s2:
                    s3 = re.sub(r'U\. S\.', 'U S', s2)
                    s2 = s3
                if 'B.E.' in s2:
                    s3 = re.sub(r'B\.E\.', 'B E', s2)
                    s2 = s3

                if 'in the U S' in s2:
                    s3 = re.sub(r'in the U S', 'in the U S.', s2)
                    s2 = s3

                res = s2.split(sep='.')
                print('res', res)
                print('}}}}}}}}}}')

                psidfin.loc[i, 'title'] = res[0]
                psidfin.loc[i, 'journal'] = res[1]
                psidfin.loc[i, 'year'] = res[2]

    for i, row in psidfin.iterrows():
        if 'Forthcoming' in row['journal']:
            print(psid.loc[i, 'info2 split'])



    print('=================')
    print(nlsy)

    test = pd.DataFrame(nlsy[0].str.split('\"').tolist(), columns=['authors', 'title', 'info'])
    #filt= [False if s is None else True for s in test['info'].values]
    #print(test.loc[filt,:])
    test2 = pd.DataFrame(test.loc[:, 'info'].str.split("\(|\)").tolist(), columns=['journal', 'date', 'page', 'b1', 'b2'])
    test2[['date1', 'year']] = test2['date'].str.rsplit(' ', n=1, expand=True)
    #print('year', test2['year'])
    filt = [True if r is None else False for r in test2['year']]
    #print('filt', sum(filt))
    # print(psid)
    test2.loc[filt, 'year'] = test2.loc[filt, 'date1']
    #print('filt yr', test2.loc[filt, 'year'])
    #print('test', test2)
    filt2 = [True if r is None else False for r in test2['year']]
    #print(test2.loc[filt2, :])
    #print('f2', sum(filt2))
    #print(test2)
    test2[['authors', 'title']] = test[['authors', 'title']]
    #print(test2.columns)
    test3 = test2[['title', 'journal', 'authors', 'year']]
    #psid.to_csv('psid_clean.csv', index=False)
    return test3, psidfin


if __name__ == '__main__':
    #finaldf, failed = extract()
   #finaldf.to_csv('../citations.csv', index=False)
    #print(failed)
    nlsy, psid = twotocsv()
    print('nlsy')
    print(nlsy)
    print('psid')
    print(psid)
    nlsy.to_csv('nlsy_cleaned.csv', index=False, )
    # psid.to_csv('psid_cleaned.csv', index=False, )
