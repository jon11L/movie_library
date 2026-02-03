from django.db import connection
from django.conf import settings

import time


def timer(func):
    '''
    - Timer allow to calculate the time the wrapped function took to execute
    - Return a print statement of the time's execution
    '''
    def wrapper(*args, **kwargs):
        start_time = time.time()

        result = func(*args, **kwargs) # Call the wrapped function

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"-- processing page time: {elapsed_time:.2f} seconds. --\n")

        return result # Return first the result of the wrapped function
    return wrapper # Then return the Wrapper // timer


def num_queries(func):
    '''
    - num_queries allow to calculate the amount of queries to the DB.
    - Return a print statement of the queries executed
    '''
    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs) # Call the wrapped function

        # Debug: Print number of queries
        if settings.DEBUG:
            print(
                "\n==================\n"
                f"- Number of queries: {len(connection.queries)}"
            )

            for query in connection.queries:
                print(f"--> {query['sql']}")
            print("=======================\n")

        return result # Return first the result of the wrapped function
    return wrapper # Then return the Wrapper // queries made
