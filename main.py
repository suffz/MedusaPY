try:
    import socket
    import urllib
    import os
    from os import path, system
    import re
    from time import time, sleep, perf_counter
    from datetime import datetime
    import asyncio
    import ssl
    from colorama import Fore
    import requests
    import json
except ImportError:
    print("Trying to install the missing modules and libs. Run the program after the installing is done!")
    system("sudo apt install libcurl4-gnutls-dev librtmp-dev")
    system("py -m pip install -r requirements.txt")
    system("python -m pip install -r requirements.txt")
    system("python3 -m pip install -r requirements.txt")
    input("Finished installing required modules, press enter to continue...")
    quit()

os.system("")
global name
global delay
global dropTime
global bearer
global email
global password
global accounts_split

print(f'''
{Fore.LIGHTRED_EX}███╗   ███╗███████╗██████╗ ██╗   ██╗███████╗ █████╗ {Fore.LIGHTMAGENTA_EX}    ██████╗ ██╗   ██╗
{Fore.LIGHTRED_EX}████╗ ████║██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗{Fore.LIGHTMAGENTA_EX}    ██╔══██╗╚██╗ ██╔╝
{Fore.LIGHTRED_EX}██╔████╔██║█████╗  ██║  ██║██║   ██║███████╗███████║{Fore.LIGHTMAGENTA_EX}    ██████╔╝ ╚████╔╝ 
{Fore.LIGHTRED_EX}██║╚██╔╝██║██╔══╝  ██║  ██║██║   ██║╚════██║██╔══██║{Fore.LIGHTMAGENTA_EX}    ██╔═══╝   ╚██╔╝  
{Fore.LIGHTRED_EX}██║ ╚═╝ ██║███████╗██████╔╝╚██████╔╝███████║██║  ██║{Fore.LIGHTMAGENTA_EX}    ██║        ██║   
{Fore.LIGHTRED_EX}╚═╝     ╚═╝╚══════╝╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝{Fore.LIGHTMAGENTA_EX}    ╚═╝        ╚═╝   
                                                                         {Fore.RESET}''')


async def check():
    for i in range(10):
        uri = urllib.parse.urlparse('https://api.minecraftservices.com/minecraft')
        reader, writer = await asyncio.open_connection(uri.hostname, 443, ssl=True)
        writer.write(f"GET {uri.path or '/'} HTTP/1.1\r\nHost:{uri.hostname}\r\n\r\n".encode())
        pingtimes = []
        start = perf_counter()
        await writer.drain()
        time1 = time()
        await reader.read(1)
        end = perf_counter()
        time2 = time()
        pingtimes.append(time2 - time1)
        print(f"[{Fore.CYAN}~{Fore.RESET}] Took {int((time2 - time1) * 1000)}ms")
        offset = int(sum(pingtimes) / len(pingtimes) * 10000 / 2)
    print(f"\n* [{Fore.CYAN}!{Fore.RESET}] Recommended delay: {offset + 10}\n")
    return round(offset)


def accountCheck():
    filesize = path.getsize("accounts.txt")
    try:
        if filesize == 0:
            print(f"[{Fore.BLUE}INFO{Fore.RESET}] Please enter an input into your accounts folder!")
            exit()
    except Exception:
        print(f"[{Fore.BLUE}INFO{Fore.RESET}] Please add an accounts.txt!")
        exit()


def mfaLogin():
    try:
        f = open("accounts.txt", "r")
        accounts = f.read()
        global accounts_split
        accounts_split = re.split(':|\n', accounts)
        global email
        email = accounts_split[0]
        global password
        password = accounts_split[1]

        responseJSON = requests.post("https://authserver.mojang.com/authenticate",
                                     json={"agent": {"name": "Minecraft", "version": 1}, "username": email,
                                           "password": password})
        parsedJSON = json.loads(responseJSON.text)
        global bearer
        bearer = parsedJSON['accessToken']

        secure = requests.get("https://api.mojang.com/user/security/location", headers={'Authorization': bearer})
        ncE = requests.get("https://api.minecraftservices.com/minecraft/profile/namechange",
                           headers={"Authorization": f"Bearer {bearer}"}).json()
        Security = requests.get("https://api.mojang.com/user/security/challenges",
                                headers={"Authorization": f"Bearer {bearer}"}).json()


        answers = []
        if Security == []:
            if ncE['nameChangeAllowed'] is False:
                print(f"\n* [{Fore.CYAN}!{Fore.RESET}] Account {email} is not eligible for name change!")
                quit()
            else:

                print(f"\n* [{Fore.CYAN}+{Fore.RESET}] Successfully logged into account {email}\n")
        else:
            try:
                accs = 1
                for x in range(3):
                    accs += 1
                    answers.append({"id": Security[x]["answer"]["id"], "answer": accounts_split[accs]})
                Send = requests.post("https://api.mojang.com/user/security/location",
                                     headers={"Authorization": f"Bearer {bearer}"}, json=answers)
                if Send.status_code == 403:
                    print(f"\n* [{Fore.CYAN}!{Fore.RESET}] Failed to authorize your account, check the inputted answers.")
                    quit()
                if Send.status_code == 204:
                    print(f"\n* [{Fore.CYAN}+{Fore.RESET}] Successfully authorized and logged into the account - {email}")
                    print()
            except IndexError:
                print(f"\n* [{Fore.CYAN}!{Fore.RESET}] The account {email} has security questions.. you did not include them!")
                quit()
    except KeyError:
        print(f"\n* [{Fore.CYAN}!{Fore.RESET}] The account {email} does not work.")
        quit()


def socketSending():
    sendamount = 0
    stoplooping = 0
    success = 0
    data = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('api.minecraftservices.com', 443))
        context = ssl.create_default_context()
        with context.wrap_socket(s, server_hostname='api.minecraftservices.com') as ss:
            for i in range(2):
                snipetime2 = dropTime - time() - (delay / 1000)
                sleep(snipetime2)
                while sendamount < 2:
                    ss.send(b'PUT /minecraft/profile/name/' + bytes(name,
                                                                    'utf-8') + b' HTTP/1.1\r\nHost: api.minecraftservices.com\r\nAuthorization: Bearer ' + bytes(
                        bearer, 'utf-8') + b'\r\n\r\n')

                    print(f"[{Fore.CYAN}INFO{Fore.RESET}] Sent request - {time()}")
                    sendamount += 1
                print()
                while success < 1:
                    while stoplooping < 2:
                        data = ss.recv(10000).decode("utf-8")
                        print(f"[{Fore.CYAN}{data[9:12]}{Fore.RESET}] Recieved Request - {time()}")
                        stoplooping += 1
                        if data[9:12] == '200':
                            print()
                            print(f"[{Fore.CYAN}!{Fore.RESET}] Successfully sniped: {name}!")
                            success += 1
                            stoplooping += 2
                        if data[9:12] == '429':
                            print(f"[{Fore.CYAN}X{Fore.RESET}] Rate limited!")
                            stoplooping += 1
                    quit()
                    try:
                        system("pause")
                        quit()
                    except Exception:
                        quit()


def socketSendingGC():
    sendamount = 0
    stoplooping = 0
    success = 0
    data = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('api.minecraftservices.com', 443))
        context = ssl.create_default_context()
        with context.wrap_socket(s, server_hostname='api.minecraftservices.com') as ss:
            for i in range(6):
                snipetime2 = dropTime - time() - (delay / 1000)
                sleep(snipetime2)
                while sendamount < 6:
                    data_to_send = (bytes("\r\n".join(
                        ["POST /minecraft/profile HTTP/1.1", "Host: api.minecraftservices.com",
                         "Content-Type: application/json", f"Authorization: Bearer {bearer}",
                         "Content-Length: %d" % len('{"profileName": "%s"}' % name), "",
                         '{"profileName": "%s"}' % name]), "utf-8"))
                    ss.send(data_to_send)

                    print(f"[{Fore.CYAN}INFO{Fore.RESET}] Sent request - {time()}")
                    sendamount += 1
                print()
                while success < 1:
                    while stoplooping < 6:
                        data = ss.recv(10000).decode("utf-8")
                        print(f"[{Fore.RED}{data[9:12]}{Fore.RESET}] Recieved Request - {time()}")
                        if data[9:12] == '200':
                            print()
                            print(f"[{Fore.GREEN}{data[9:12]}{Fore.RESET}] Successfully sniped: {name}!")
                            success += 1
                            stoplooping += 2
                        if data[9:12] == '429':
                            print(f"[{Fore.RED}{data[9:12]}{Fore.RESET}] Rate limited!")
                            stoplooping += 1
                    quit()
                    try:
                        system("pause")
                        quit()
                    except Exception:
                        quit()


def snipeTime():
    sleeping = dropTime - time() - (delay / 1000)

    print(f"[{Fore.CYAN}INFO{Fore.RESET}] Sleeping for: {sleeping} Seconds\n")

    sleep(sleeping - 15)


def start():
    accountCheck()
    i = 0
    print(
        f"[{Fore.CYAN}INFO{Fore.RESET}] Ver: \n\n[{Fore.CYAN}1{Fore.RESET}]: SFA/MFA\n[{Fore.CYAN}2{Fore.RESET}]: GC\n[{Fore.CYAN}3{Fore.RESET}]: MS\n")
    option = int(input(f"{Fore.RED}>: {Fore.RESET}"))
    print("\n")
    print(f"[{Fore.CYAN}INFO{Fore.RESET}] Enter Name: ")
    global name
    name = str(input(f"{Fore.RED}>: {Fore.RESET}"))
    print(f"[{Fore.CYAN}INFO{Fore.RESET}] Enter delay: ")
    global delay
    delay = float(input(f"{Fore.RED}>: {Fore.RESET}"))
    print(f"[{Fore.CYAN}INFO{Fore.RESET}] Enter Droptime [UNIX]: ")
    global dropTime
    dropTime = int(input(f"{Fore.RED}>: {Fore.RESET}"))

    if option == 1:
        mfaLogin()
        snipeTime()
        socketSending()
    elif option == 2:
        print(f"[{Fore.CYAN}INFO{Fore.RESET}] Enter Bearer: ")
        global bearer
        bearer = str(input(f"{Fore.RED}>: {Fore.RESET}"))
        snipeTime()
        socketSendingGC()
    elif option == 3:
        print(f"[{Fore.CYAN}INFO{Fore.RESET}] Enter Bearer: ")
        bearer = str(input(f"{Fore.RED}>: {Fore.RESET}"))
        snipeTime()
        socketSending()

    else:
        exit(print(f"{Fore.RED}ERROR:{Fore.RESET} {Fore.CYAN}Incorrect Input{Fore.RESET}"))


loop = asyncio.get_event_loop()
loop.run_until_complete(check())
start()
