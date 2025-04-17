import os
import sys
import pandas as pd


def redact(data_path):
    """
    Collate the cleaned data sets into a single dataset and shuffle

    Args:
        data_path (folder): Dataset folder path
    """

    def redact_source_real(article):
        source = article['source']
        text = article['text']

        source_idx = text.find(source) + len(source)
        dash_idx = text.find('-', source_idx)

        if dash_idx == -1:
            # remove source if no trailing dash found
            return text.replace(source, '')
        else:    
            # remove the source and everything that comes before it
            return text[dash_idx+1:].lstrip()

    def redact_source_fake(article):
        source = article['source']
        text = article['text']

        # find the last occurrence of the source and remove everything after it
        source_idx = text.rfind(source)
        redacted = text[:source_idx].rstrip()

        # redact other occurrences of the source
        return redacted.replace(source, '')

    path_real = os.path.join(data_path, "real.csv")
    path_fake = os.path.join(data_path, "fake.csv")

    real = pd.read_csv(path_real)
    fake = pd.read_csv(path_fake)

    # redact sources
    real['text'] = real.apply(redact_source_real, axis=1)
    fake['text'] = fake.apply(redact_source_fake, axis=1)

    # save redacted datasets
    os.makedirs(os.path.join("data", "redacted"), exist_ok=True)
    real_out = os.path.join("data", "redacted", "real.csv")
    fake_out = os.path.join("data", "redacted", "fake.csv")

    real.to_csv(real_out, index=False)
    fake.to_csv(fake_out, index=False)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Arguments error.\n")
        sys.stderr.write("Usage: python3 src/prepare/redact.py path-to-data\n")
        sys.exit(1)

    data_path = sys.argv[1]
    redact(data_path)    

if __name__ == "__main__":
    main()
