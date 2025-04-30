import numpy as np

def to_numpy(text_batch):
    """
    Convert the input text batch to a numpy array.

    Args:
        text (str): Input text.

    Returns:
        str: Preprocessed text.
    """
    return np.array([text.lower().strip() for text in text_batch])