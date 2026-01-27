from django.db import connection
from django.conf import settings

import time


def timer(func):
    '''
    Timer allow to calculate the time the wrapped function took to execute
    Return a print statement of the time's execution
    '''
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result = func(*args, **kwargs) # Call the rapped function

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"-- processing page time: {elapsed_time:.2f} seconds. --\n")

        return result # Return first the result of the wrapped function
    return wrapper




def num_queries(func):
    '''
    num_queries allow to calculate the amount of queries to the DB done in the wrapped function
    Return a print statement of the queries executed
    '''
    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs) # Call the rapped function

        # Debug: Print number of queries
        if settings.DEBUG:
            print(f"==================\nNumber of queries: {len(connection.queries)}")
            for query in connection.queries:
                print(query['sql'])
            print("=======================\n")

        return result # Return first the result of the wrapped function
    return wrapper
