import nltk
import os
import re
import pandas as pd
import matplotlib.pyplot as plt


def check():
    threshold = .4
    removed = pd.DataFrame(columns=['title', 'download title'])
    bare_details = pd.read_csv('../../input_data/fsrdc_papers_bare_details_2.csv', header=0, error_bad_lines=False)
    spellings = pd.read_csv('../../input_data/spellingchecks.csv', header=0, error_bad_lines=False)

    # print(os.getcwd())
    if os.getcwd() != '/Users/jiyoojeong/Desktop/C/FSRDC_Papers/output_data/raw':
        os.chdir('output_data/raw')
    ids = [i for i in os.listdir() if '.txt' in i]
    simscores = []
    for fname in ids:
        artid = re.sub(r'\.txt', '', fname)

        titleid = bare_details.loc[bare_details['article_id'] == int(artid), ['article_id', 'title']]
        title = titleid['title'].values[0]
        #print(title)
        f = open(fname, "r")
        download_title = re.sub('For:', '', f.readline())
        download_title = download_title.lower()
        #print(download_title)
        similarity_score = 1 - nltk.edit_distance(title.lower(), download_title) / len(download_title)
        #print(similarity_score)
        simscores.append(similarity_score)
        # delete
        if similarity_score < threshold:
            if title not in download_title and download_title not in title:
                # passes
                #print("------ REMOVED -------")
                os.remove(fname)
                simscores.remove(similarity_score)
                removed = removed.append({'title': title, 'download title': download_title}, ignore_index=True)


    plt.hist(simscores)
    plt.show()
    print('avg:', sum(simscores)/len(simscores))

    save = pd.DataFrame(columns=['aid', 'title', 'reason'])
    alldowns = os.listdir()
    alldowns = [re.sub('\.txt', '', t) for t in alldowns]
    mispel = spellings.loc[:, 'aid'].values
    for idx, row in bare_details.iterrows():
        aid = row['article_id']
        title = row['title']
        # print(aid)
        if aid not in alldowns and aid in mispel:
            print('no wos', aid)
            save = save.append({'aid': aid, 'title': title, 'reason': 'Not in WOS or Misspelling'}, ignore_index=True)
        elif aid not in alldowns:
            print('no cit', aid)
            save = save.append({'aid': aid, 'title': title, 'reason': 'No citations'}, ignore_index=True)

    save.to_csv('../../input_data/no_results.csv', index=False)
    return removed


if __name__ == '__main__':
    try:
        os.chdir('output_data/raw')
    finally:
        lenprior = len(os.listdir())
        rems = check()
        print('files befor:', lenprior)
        print('files after:', len(os.listdir()))
        print('num removed:', lenprior - len(os.listdir()))
        print(rems)
