def isEnglish(word):
    """check if given input is in English"""
    try:
        word.decode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        return True