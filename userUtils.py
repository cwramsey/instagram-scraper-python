import requests, random, progressbar, time, ConfigParser
from tokenUtils import *
from dbUtils import dbInsert
from multiprocessing import Process, Lock, Queue, current_process
from loggingUtils import getLogger

logger = getLogger(__name__)

def config():
    c = ConfigParser.ConfigParser()
    opts = c.read(open('./config.ini'))
    print opts
    quit()

def getUser(id, token):
    global logger
    payload = {'access_token': token['token']}
    url = "https://api.instagram.com/v1/users/{}".format(str(id))

    r = requests.get(url, params=payload)

    if r.status_code != 200:
        logger.warning("Error getting user {}: {}".format(id, r.text))
        return False
    else:
        logger.info("Successfully got user {}: {}".format(id, r.text))
        return r.json()

def user_worker(work_queue, done_queue):
    """
        Checks for users in a multiprocessing thingy
    """
    for data in iter(work_queue.get, 'STOP'):
        user = getUser(data['id'], data['token'])

        if user and 'data' in user:
            done_queue.put(format_user(user))

    return True

def get_users(tokens, user_ids):
    """
        Runs 50 processes to check all tokens really freakin' fast
    """
    user_ids = range(user_ids, user_ids + 1000)
    workers = 50
    work_queue = Queue()
    done_queue = Queue()
    processes = []

    for user_id in user_ids:
        updated_tokens = getRandomToken(tokens)
        token = updated_tokens['chosen_token']
        tokens = updated_tokens['all_tokens']

        work_queue.put({'id': user_id, 'token': token})

    for w in xrange(workers):
        p = Process(target=user_worker, args=(work_queue, done_queue))
        p.start()
        processes.append(p)
        work_queue.put('STOP')

    for p in processes:
        p.join()

    done_queue.put('STOP')

    for user in iter(done_queue.get, 'STOP'):
        dbInsert(user)

    return True

def format_user(user):
    return [user['data']['username'], user['data']['full_name'], user['data']['bio'], user['data']['website'], user['data']['profile_picture'], user['data']['counts']['media'], user['data']['counts']['followed_by'], user['data']['counts']['follows'], user['data']['id']]
