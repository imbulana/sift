import os
import sys
import pandas as pd


SOURCES = [
    '21st century wire', 'reason.com', 'hammond news', 'alternate current radio', '21wire', '21wire.tv',
    'fox news', 'news360', 'the guardian', 'wfb', 'dispatch', 'the american mirror', 'ijreview',
    'cnsnews', 'gateway pundit', 'daily mail', 'washington examiner', 'express uk', 'ktar news',
    'cnn', 'conservative treehouse', 'daily caller', 'the blaze', 'cbc', 'tmz', 'vulture', 'kmov',
    'the hayride', 'breitbart', 'brietbart', 'gp', 'mr. conservative', 'fox 2', 'chron', 'ap', 'abc news',
    'the olympian', 'the hill', 'deadline', 'tampa bay', 'politico', 'wt', 'zero hedge', 'nyp',
    'hollywood reporter', 'wxyz', 'examiner.com', 'bbc', 'la times', 'getty', 'flickr', 'screengrab',
    'youtube', 'twitter', 'facebook', 'wall street journal', 'nbcdfw', 'nyt', 'fortune',
    'washington free beacon', 'huffington post', 'bizpac review', 'washington times', 'sltrb',
    'the college fix', 'eag news', 'cnbc', 'krtv', 'bpr', 'whitehouse.gov', 'mbr', 'wesh.com',
    'screenshot', 'boston herald', 'wnd', 'wikimedia', 'politically short', 'biz pac', 'kcs', 'espn',
    'washington post', 'national review', 'reuters', 'downtrend', 'yahoo news', 'weasel zippers',
    'dfp', 'npr', 'page six', 'rcp', 'the federalist', 'tpm', 'the detroit news', 'wbrz', 
    'ny daily news', 'myfox8', 'palm beach post', 'mrctv', 'the bureau', 'detroit free press', 
    'moonbattery', 'radar online', 'gatestone institute', 'star tribune', 'business insider', 
    'the lonely conservative', 'mediaite', 'national enquirer', 'public domain', 'ai archives',
    'the lid', 'ws', 'stars and stripes', '2nd amendment files', 'israel files', 'hammond ranch',
]


def clean(data_path):
    """
    Process the input data and write the output to the output files.

    Args:
        data_path (folder): Dataset folder path
    """

    def _clean(ds):
        # to lowercase
        ds['title'] = ds['title'].str.lower()
        ds['text'] = ds['text'].str.lower()
        ds['subject'] = ds['subject'].str.lower()
        ds['date'] = ds['date'].str.lower()

        # duplicates
        # ds.duplicated().sum(), ds['text'].duplicated().sum(), ds['title'].duplicated().sum()

        # drop rows w/ duplicated text
        ds.drop_duplicates(subset='text', keep='first', inplace=True)
        ds.reset_index(drop=True, inplace=True)

        # len(ds)

        return ds

    def _get_source(text):
        # source mentioned at end of article?
        for source in SOURCES:
                if source in text[-100:]:
                    return source
        return 'other'

    path_real = os.path.join(data_path, "real.csv")
    path_fake = os.path.join(data_path, "fake.csv")


    ''' REAL NEWS ''' 

    real = pd.read_csv(path_real)
    real = _clean(real)

    # add source column
    from_reuters = real['text'].apply(lambda t: 'reuters' in t)
    # from_reuters.sum(), len(real) - from_reuters.sum()
    real['source'] = from_reuters.map({True: 'reuters', False: 'other'}) 


    ''' FAKE NEWS '''

    fake = pd.read_csv(path_fake)
    fake = _clean(fake)

    # add source column
    fake['source'] = fake['text'].apply(_get_source)

    # fake['source'].value_counts()

    # save cleaned dataset
    os.makedirs(os.path.join("data", "cleaned"), exist_ok=True)
    real_out = os.path.join("data", "cleaned", "real.csv")
    fake_out = os.path.join("data", "cleaned", "fake.csv")

    real.to_csv(real_out, index=False)
    fake.to_csv(fake_out, index=False)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Arguments error.\n")
        sys.stderr.write("Usage: python3 src/prepare/clean.py path-to-data\n")
        sys.exit(1)

    data_path = sys.argv[1]
    clean(data_path)    

if __name__ == "__main__":
    main()
