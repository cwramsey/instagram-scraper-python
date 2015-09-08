import re, requests, random, logging
from multiprocessing import Process, Lock, Queue, current_process
from loggingUtils import getLogger

logger = getLogger(__name__)

def readTokens():
    """
        Reads the tokens file and uses a regex to find the tokens in each row
    """
    file = open('tokens.csv', 'r')
    tokens = []

    for line in file:
        token = re.search(r'([0-9]+\.[a-zA-Z0-9]+\.[0-9a-zA-Z]+)', line, re.M|re.I)
        if token is not None:
            tokens.append(token.group(1))

    return tokens

def readValidTokens():
    """
        Opens the valid tokens file and creates a dict with the tokens
    """
    file = open('validTokens.txt')
    tokens = []

    for token in file:
        tokens.append({
            'token': token,
            'uses': 0
        })

    return tokens

def checkToken(token):
    """
        Hits an instagram endpoint with a token to check it's validity.
        If a 400 is returned, it's not valid.
    """
    payload = {'access_token': token}
    url = "https://api.instagram.com/v1/users/self/feed"
    r = requests.get(url, params=payload)
    result = r.json()

    if result['meta']['code'] is 200:
        return True
    else:
        return False

def writeTokenToFile(token, isValid):
    filename = 'validTokens.txt'

    if isValid is False:
        filename = 'invalidTokens.txt'

    file = open(filename, 'a')
    file.write(token)
    file.write("\n")

def getRandomToken(tokens):
    """
        Gets a random token. If a token's use count is greater than 5000, recursively get a new random
        token until you get one that isn't.
    """
    token = random.choice(tokens)

    if (token['uses'] >= 4999):
        return getRandomToken(tokens)

    #update token use count
    token['uses'] += 1
    updated_tokens = updateToken(token, tokens)

    return {
        'all_tokens': updated_tokens,
        'chosen_token': token
    }

def updateToken(token, token_list):
    """
        Finds the token in the list and updates it's count before returning the full token list
    """
    for x in token_list:
        if x['token'] == token['token']:
            x['uses'] = token['uses']

    return token_list

def token_worker(work_queue, done_queue):
    """
        Checks tokens in a multiprocessing thingy
    """
    for token in iter(work_queue.get, 'STOP'):
        isValid = checkToken(token)
        done_queue.put({'token': token,'valid': isValid})
    return True

def get_tokens():
    """
        Runs 50 processes to check all tokens really freakin' fast
    """
    global logger
    open('validTokens.txt', 'w').close()
    open('invalidTokens.txt', 'w').close()

    logger.info("Validating tokens")

    all_tokens = readTokens()
    workers = 50
    work_queue = Queue()
    done_queue = Queue()
    processes = []

    for token in all_tokens:
        work_queue.put(token)

    for w in xrange(workers):
        p = Process(target=token_worker, args=(work_queue, done_queue))
        p.start()
        processes.append(p)
        work_queue.put('STOP')

    for p in processes:
        p.join()

    done_queue.put('STOP')

    for status in iter(done_queue.get, 'STOP'):
        writeTokenToFile(status['token'], status['valid'])

    valid_tokens = readValidTokens()

    logger.info("Found {} valid tokens".format(len(valid_tokens)))

    return valid_tokens
