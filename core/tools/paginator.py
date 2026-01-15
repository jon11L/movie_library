
def page_window(current, total, size):
    '''
        - `current`: the current page being browsed
        - `total`: the total amount of pages present
        - `size`: amount of buttons to display around the current page
    '''
    start = max(current - size, 1)
    end = min(current + size, total)
    return range(start, end + 1)