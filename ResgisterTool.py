import requests 
import threading 
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Student:
    headers = {
        "Accept": 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Origin': 'https://sinhvien1.tlu.edu.vn',
        "Referer": 'https://sinhvien1.tlu.edu.vn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Te': 'trailers',
        "Connection": 'close'
        }
    
    def __init__(self, username, password):
        self.__username = username
        self.__password = password
        self.token = self.login()
        print(f'your token is: {self.token}')
        if not self.token:
            print("Login failed")
            exit()
        else:
            print("Login success")
            option = int(input("Ban muon dang ky hoc nao?\n[0] ky he \n[1] hoc ky chinh \n[*] Inssert your option: "))
            if option == 0:
                self.option = 41
            elif option == 1:
                self.option = 36
            else:
                print("Option not correct")
                exit()
            
            Student.headers["Authorization"] = self.token
            self.id = self.getIdUser()
            self.data= self.getSubjectList() 
    
    def login(self):
        data = {
        "client_id":"education_client",
        "grant_type":"password",
        "username":self.__username,
        "password":self.__password,
        "client_secret":"password"
        }
        for i in range(50):
            try:
                url = "https://sinhvien1.tlu.edu.vn:9923/education/oauth/token"
                proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
                r = requests.post(url, data=data, headers=Student.headers,proxies=proxies,timeout=200, verify=False)
                #r = requests.post(url, data=data, headers=Student.headers,timeout=200)
                t = r.json()
                token = t['token_type'] + t["access_token"]
                return token
            except requests.exceptions.ReadTimeout: 
                # handle readtimeout err using urllib3
                print('Request Time out.\nTry to reconnect: attempt ', i+1)
            except requests.exceptions.ConnectTimeout:
                print('Time out attempt ', i+1)
            except:
                print("Username or password not correct")
                return ""
        return ""
    
    def getIdUser(self):
        # get id user 
        url = 'https://sinhvien1.tlu.edu.vn:9923/education/api/users/getCurrentUser'
        # proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
        # r = requests.get(url, headers=Student.headers, proxies=proxies, verify=False,timeout=200)
        r = requests.get(url, headers=Student.headers,timeout=200)
        dataUser = r.json()
        idUser = dataUser['person']['id']
        return idUser

    def getSubjectList(self):
        url = "https://sinhvien1.tlu.edu.vn:9923/education/api/cs_reg_mongo/findByPeriod/{a}/{b}".format(a=self.id, b=self.option)
        # proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
        # r = requests.get(url, headers=Student.headers, proxies=proxies,timeout=200, verify=False)
        r = requests.get(url, headers=Student.headers,timeout=200)
        data = r.json()
        return data
    
    def showSubject(self):
        subjects = self.data['courseRegisterViewObject']["listSubjectRegistrationDtos"]
        num_subjects = len(subjects)
        columns = (num_subjects + 9) // 10  # Số lượng cột, mỗi cột tối đa 10 dòng

        # Tạo một danh sách các danh sách, mỗi danh sách con chứa tối đa 10 phần tử
        grouped_subjects = [subjects[i:i+10] for i in range(0, num_subjects, 10)]

        # In các môn học theo từng cột
        for row in range(10):
            for col in range(columns):
                index = col * 10 + row
                if index < num_subjects:
                    subject_name = subjects[index]['subjectName']
                    print(f"Subject number: [{index}] {subject_name}".ljust(50), end=' ')
            print()

    def showTimeTable(self,indexSub):
        subjectTable = self.data['courseRegisterViewObject']["listSubjectRegistrationDtos"][indexSub]['courseSubjectDtos']
        index = 0
        for i in subjectTable:
            print('Class number: [{a}]'.format(a=index))
            for j in i['timetables']:
                print('\tThu {a}: {b} den {c}'.format(a=j['weekIndex'], b=j['start'], c=j['end']) )
                print('\tTuan : {a} den {b}'.format(a=j['fromWeek'],b=j['toWeek']))
            index += 1
            print()   
            
    def send_request(self, url, json_data,num):
        try:
            proxies = { 'http':'http://127.0.0.1:8080', 'https':'http://127.0.0.1:8080'}
            
            r = requests.post(url, headers=Student.headers, json=json_data, timeout=200,proxies=proxies, verify=False)
            data_receive = r.json()
            data = data_receive['message']
            print(f'\n[m] {num}. {data}') 
        except Exception as e:
            print(f'Lỗi khi gửi yêu cầu: {e}\n ')
            
    def Register(self,indexSub,index):
        
        subjectTable = self.data['courseRegisterViewObject']["listSubjectRegistrationDtos"][indexSub]['courseSubjectDtos']
        url = 'https://sinhvien1.tlu.edu.vn:9923/education/api/cs_reg_mongo/add-register/{a}/{b}'.format(a=self.id, b=self.option)
        json = subjectTable[index]

        num = int(input("[****] Insert number of request: "))
        print('Sending request...\n___________________________________')

        threads = []
        while True:
            for _ in range(num):
                thread = threading.Thread(target=self.send_request, args=(url, json, _))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
            
            ans = input('\nDo you want to continue?(y/n): ')
            if ans.lower() != 'y':
                break
            else:
                continue
            


art = """
 ____   _               _     __          __ _         _
|  _ \ | |             | |    \ \        / /(_)       | |
| |_) || |  __ _   ___ | | __  \ \  /\  / /  _  _ __  | |_   ___  _ __
|  _ < | | / _` | / __|| |/ /   \ \/  \/ /  | || '_ \ | __| / _ \| '__|
| |_) || || (_| || (__ |   <     \  /\  /   | || | | || |_ |  __/| |
|____/ |_| \__,_| \___||_|\_\     \/  \/    |_||_| |_| \__| \___||_|

                                                Code by TMT
    """
def menu():
    print('[1] Show available subjects\n[2] Show subject time-table\n[3] Register an subject')
    
    
if __name__ == "__main__":
    print(art)
    username = '2251272726'
    password = '001204038938'
    
    student = Student(username, password)
    if not student.token:
        exit()
    while True:
        print(art)
        menu()
        option = int(input("Your option: "))
        if option == 1:
            student.showSubject()
        elif option == 2:
            indexSub = int(input("Insert subject number: "))
            student.showTimeTable(indexSub)
        elif option == 3:
            indexSub = int(input("Insert subject number: "))
            index = int(input("Insert class number: "))
            student.Register(indexSub, index)
        else:
            print("Option not correct")
            continue
        