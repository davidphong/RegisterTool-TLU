import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def getToken(user_name, password):
    headers = {
        "Accept": 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Origin': 'https://sinhvien2.tlu.edu.vn',
        "Referer": 'https://sinhvien2.tlu.edu.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Te': 'trailers',
        "Connection": 'close'
    }

    data = {
        "client_id":"education_client",
        "grant_type":"password",
        "username":user_name,
        "password":password,
        "client_secret":"password"
    }
    for i in range(10):
        try:
            url = "https://sinhvien2.tlu.edu.vn:9923/education/oauth/token"
            # proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
            # r = requests.post(url, data=data, headers=headers,proxies=proxies, verify=False)
            r = requests.post(url, data=data, headers=headers,timeout=5)
            t = r.json()
            token = t['token_type'] + t["access_token"]
            return token
        except requests.exceptions.ReadTimeout: 
            # handle readtimeout err using urllib3
            print('Request Time out.\nTry to reconnect: Attemp ', i+1)
        except requests.exceptions.ConnectTimeout:
            print('time out attemp ', i+1)
        except:
            print("Username or password not correct")
            return ""
    return ""

def defauteHeaders(token):
    headers = {
        "Host": "sinhvien2.tlu.edu.vn:9923",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "application/json, text/plain, */*",
        "Authorization": token,
        "Origin": "https://sinhvien2.tlu.edu.vn",
        "Referer": "https://sinhvien2.tlu.edu.vn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "close"
    }
    return headers

def getIdUser(headers):
    # get id user 
    url = 'https://sinhvien2.tlu.edu.vn:9923/education/api/users/getCurrentUser'
    # proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
    # r = requests.get(url, headers=headers, proxies=proxies, verify=False)
    r = requests.get(url, headers=headers)
    dataUser = r.json()
    idUser = dataUser['person']['id']
    return idUser

def getSubjectList(headers):
    idUser = getIdUser(headers)
    url = "https://sinhvien2.tlu.edu.vn:9923/education/api/cs_reg_mongo/findByPeriod/{a}/36".format(a=idUser)
    # proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
    # r = requests.get(url, headers=headers, proxies=proxies, verify=False)
    r = requests.get(url, headers=headers)
    data = r.json()
    return data

def showTimeTable(indexSub,headers):
    data = getSubjectList(headers)
    subjectTable = data['courseRegisterViewObject']["listSubjectRegistrationDtos"][indexSub]['courseSubjectDtos']
    index = 0
    for i in subjectTable:
        print('Class number: [{a}]'.format(a=index))
        for j in i['timetables']:
            print('\tThu {a}: {b} den {c}'.format(a=j['weekIndex'], b=j['start'], c=j['end']) )
            print('\tTuan : {a} den {b}'.format(a=j['fromWeek'],b=j['toWeek']))
        index += 1
        print()   

def Register(indexSub,index,headers):
    data = getSubjectList(headers)
    idUser = getIdUser(headers)
    
    subjectTable = data['courseRegisterViewObject']["listSubjectRegistrationDtos"][indexSub]['courseSubjectDtos']
    url = 'https://sinhvien2.tlu.edu.vn:9923/education/api/cs_reg_mongo/add-register/{a}/36'.format(a=idUser)
    json = subjectTable[index]

    num = int(input("[****] Insert number of request: "))
    print('Sending request...\n___________________________________\n')
    for i in range(num):
        # proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
        # r = requests.post(url, headers=headers, json=json, proxies=proxies, verify=False)
        r = requests.post(url, headers=headers, json=json)
        dataRevice = r.json()
        print('[m] ',dataRevice['message'])

def menu():
    print('[1] Show available subjects\n[2] Show subject time-table\n[3] Register an subject')

def main():
    art = """
 ____   _               _     __          __ _         _
|  _ \ | |             | |    \ \        / /(_)       | |
| |_) || |  __ _   ___ | | __  \ \  /\  / /  _  _ __  | |_   ___  _ __
|  _ < | | / _` | / __|| |/ /   \ \/  \/ /  | || '_ \ | __| / _ \| '__|
| |_) || || (_| || (__ |   <     \  /\  /   | || | | || |_ |  __/| |
|____/ |_| \__,_| \___||_|\_\     \/  \/    |_||_| |_| \__| \___||_|

                                                Code by TMT
    """
    print(art)
    username = input('User name: ')
    password = input('Password: ')
    token = getToken(username, password)
    if len(token) > 1:
        print("Login success !")
        print('Your token is: '+token)
        while True:
            headers = defauteHeaders(token)
            menu()
            option = int(input("[*] Insert your option: "))
            if option == 1:
                data = getSubjectList(headers)
                index = 0
                for i in data['courseRegisterViewObject']["listSubjectRegistrationDtos"]:
                    print('Subject number: [{a}]'.format(a=index), ' ', i['subjectName']) # in ra ten cac mon hoc 
                    index += 1
                print("")
            elif option == 2:
                indexSub = int(input("[**] Insert subject number: "))
                showTimeTable(indexSub,headers)
            elif option == 3:
                indexSub = int(input("[**] Insert subject number: "))
                index = int(input("[***] Insert class number: "))
                Register(indexSub,index,headers)
            else:
                break
            print(art)
    else:
        return
    
main()
