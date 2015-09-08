#!/usr/bin/python
from tokenUtils import *
from userUtils import *
import time

if __name__ == '__main__':
    #Get valid tokens from the token file
    valid_tokens = get_tokens()
    user_count = 1

    #We're grabbing users in batches of 1k, so loop through until we hit the limit.
    while user_count <= 1000000000: #goes through first billion users
        get_users(valid_tokens, user_count)
        user_count += 1000
