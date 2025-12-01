import random
import datetime


def get_page(endpoint):
    ''' 
    Return a random page from a variable amount\n
    according to the endpoint selected.\n
    if function run during specific dates. then fetching with Top pages '1 to 5'
    '''
    max = 0
    prime_date = check_date_prime()

    if prime_date:
        return random.randint(1, 5) # Randomly select a page

    if endpoint == "now_playing": # Movie
        return random.randint(5, 200)
    elif endpoint == "upcoming" or endpoint == "on_the_air": # Movie, serie
        return random.randint(5, 50)
    elif endpoint == "top_rated": # Serie
        return random.randint(5, 100)
    elif endpoint == "airing_today": # Serie
        return random.randint(5, 12) # this endpoint pages number seem to change regularly
    else:
        return random.randint(1, 500)


def check_date_prime():
    '''
    - Check todays's date and if in selected days return True else False.
    '''
    today = datetime.date.today()
    if today.day in [1, 5, 10, 15, 20, 25]:
        print(f"-- special days !!!!")
        return True

    return False