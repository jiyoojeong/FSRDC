import nltk
import os
import re
import pandas as pd
import matplotlib.pyplot as plt


def check():
    threshold = .4
    bare_details = pd.read_csv('../../input_data/fsrdc_papers_bare_details_2.csv', header=0, error_bad_lines=False)
    # print(os.getcwd())
    if os.getcwd() != '/Users/jiyoojeong/Desktop/C/FSRDC_Papers/output_data/raw':
        os.chdir('output_data/raw')
    ids = [i for i in os.listdir() if '.txt' in i]
    simscores = []
    for fname in ids:
        artid = re.sub(r'\.txt', '', fname)

        titleid = bare_details.loc[bare_details['article_id'] == int(artid), ['article_id', 'title']]
        title = titleid['title'].values[0]
        print(title)
        f = open(fname, "r")
        download_title = re.sub('For:', '', f.readline()).lower().lstrip()
        print(download_title)
        similarity_score = 1 - nltk.edit_distance(title.lower(), download_title) / len(download_title)
        print(similarity_score)
        simscores.append(similarity_score)
        # delete
        if similarity_score < threshold:
            if title not in download_title and download_title not in title:
                # passes
                # print("------ CHECK THIS -------")
                os.remove(fname)
                simscores.remove(similarity_score)

    plt.hist(simscores)
    plt.show()


if __name__ == '__main__':
    try:
        os.chdir('output_data/raw')
    finally:
        print('files befor:', len(os.listdir()))
        check()
        print('files after:', len(os.listdir()))