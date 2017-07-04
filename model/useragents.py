import random

def get():
    """return ramdomly chosen useragent"""
    return random.choice(useragents)


useragents = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'
    }
]
