import re
import pandas as pd

final_search = pd.read_csv('input_data/to_find_final_2.csv', header=0)
tnew = []
for idx, row in final_search.iterrows():
    ogt = row['title_original']
    t = row['Title']
    if re.search('-', ogt):
        print('------------OGT TO T CHANGE -----------')
        print(ogt)
        print(t)
        tn = re.sub(r'[^A-Za-z0-9\s]', ' ', ogt)
        print(tn)
        tnew.append(tn)
    else:
        tnew.append(t)

final_search['Title'] = tnew
final_search['abstract'] = 0

final_search.to_csv('input_data/to_find_final_3.csv', index=False)


