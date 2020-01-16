"""
    pip install mysql.connector
"""
import cpuinfo
import executor
import oui
import json
import os
import time

import mysql.connector



def fileToMacSet(filename):
    # 덤프받은 파일을 파싱해서 딕셔너리 구조로 리턴
    with open(filename, 'r') as f:
        maclist = f.readlines()
    return set([x.strip() for x in maclist])



def loadConfig(config_file):
    # 설정 파일을 읽는다.
    with open( config_file ) as json_execfile:
        config = json.load(json_execfile)

    with open( config['cellphone'] ) as json_execfile:
        phonedb = json.load(json_execfile)
    return config, phonedb
        


def capture(config):
    # 패킷을 캡처한다.
    print('capture')
    cmd = 'tshark -I -i {} -a duration:{} -w {}'.format(config['nic'], config['duration'], config['dump_file'])
    result, error = executor.blockexec(cmd)
    if config['verbose']=='True':
        print('result: ', result)
        print('error:  ', error)

    return result, error



def readcapfile(config):
    # 캡처한 파일을 파싱하기 위해 읽어들인다(필터포함)
    print('read')
    cmd = 'tshark -r {} -T {} -e {} -e {} -e {}'.format(config['dump_file'],config['fields'], config['sa'], config['bssid'], config['dbm'])
    result, error = executor.blockexec(cmd)
    if config['verbose']=='True':
        print('result: ', result)
        print('error:  ', error)

    return result, error



def getOuidb(ouifile):
    # 핸드폰의 맥 정보와 관련된 oui 디비를 읽어들인다
    try:
        oui.download_oui(ouifile)
    except:
        pass

    ouidb = oui.load_dictionary(ouifile)
    return ouidb



def findPhone(config, ouidb, phonedb, foundMacs):
    # 파싱한 문자열을 통해 찾고자 하는 맥주소 패턴의 핸드폰들이 있는지 찾는다
    cellphone = phonedb['cellphone']
    cellphone_people = []
    for mac in foundMacs:
        oui_id = 'Not in OUI'
        if mac[:8] in ouidb:
            oui_id = ouidb[mac[:8]]
        
        if config['verbose']=='True':
            print(mac, oui_id, oui_id in cellphone)

        nearby = int(config['nearby'])

        if oui_id in cellphone:
            if not nearby or (nearby and foundMacs[mac] > -70):
                cellphone_people.append(
                    {'company': oui_id, 'rssi': foundMacs[mac], 'mac': mac})
    
    return cellphone_people



def parse(result):
    # 캡처한 패킷 캡처파일을 해당 조건의 필터에 맞추어 파싱한다.
    foundMacs = {}
    for line in result.split('\n'):
        if line.strip() == '':
            continue
        mac = line.split()[0].strip().split(',')[0]
        dats = line.split()
        if len(dats) == 3:
            if ':' not in dats[0] or len(dats) != 3:
                continue
            if mac not in foundMacs:
                foundMacs[mac] = []
            dats_2_split = dats[2].split(',')
            if len(dats_2_split) > 1:
                rssi = float(dats_2_split[0]) / 2 + float(dats_2_split[1]) / 2
            else:
                rssi = float(dats_2_split[0])
            foundMacs[mac].append(rssi)

    for key, value in foundMacs.items():
        foundMacs[key] = float(sum(value)) / float(len(value))

    return foundMacs



def saveToMaria(mydb, sqllist):
    # mariadb에 측정 결과 저장하기
    mycursor = mydb.cursor()
    for sql in sqllist:
        mycursor.execute(sql)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
    return mycursor.rowcount




def getnerateSQL(TABLE_NAME, jsondata):
    # 해당 테이블에 insert하는 구문을 딕셔너리 jsondata를 기준으로 생성함
    # sql문장의 list로 만들어짐
    sqlstatement = []

    print(type(jsondata), jsondata)
    for jsondict in jsondata:
        print(type(jsondict), jsondict)
        keylist = "("
        valuelist = "("
        firstPair = True
        
        for key, value in jsondict.items():
            if not firstPair:
                keylist += ", "
                valuelist += ", "
            firstPair = False
            keylist += key
            if type(value)==str:
                valuelist += "'" + value + "'"
            else:
                valuelist += str(value)
        keylist += ', '
        keylist += 'cpuid'
        keylist += ', '
        keylist += 'epoch'
        keylist += ")"
        valuelist += ",'"
        valuelist += cpuinfo.getCPUiD()
        valuelist += "','"
        valuelist += cpuinfo.getDateTimestr()
        valuelist += "')"

        sql = "INSERT INTO " + TABLE_NAME + " " + keylist + " VALUES " + valuelist

        sqlstatement.append( sql )

        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  ', sqlstatement)
    
    return sqlstatement




def doit():
    # 설정 파일 정보 로드
    config_file = os.getcwd() + '/' + cpuinfo.getCPUiD() + '.json'
    config, phonedb = loadConfig(config_file)

    # db접속
    mydb = mysql.connector.connect(
    host=config['dbhost'],
    user=config['dbuser'],
    passwd=config['dbpasswd'],
    database=config['database'],
    port=int(config['dbport'])
    )

    # 캡처
    result, _ = capture(config)

    # 캡처파일 파싱을 위해 로드
    result, _ = readcapfile(config)

    # 파싱
    foundMacs = parse(result)

    # ouidb 파일 로드
    ouidb = getOuidb('oui.txt')

    # 주변의 핸드폰을 찾아내 딕셔너리의 리스트에 담아 리턴
    cellphone_people = findPhone(config, ouidb, phonedb, foundMacs)

    # if sort:
    cellphone_people.sort(key=lambda x: x['rssi'], reverse=True)

    # if verbose:
    json_data = json.dumps(cellphone_people, indent=2)
    print(type(json_data), json_data)
    print(type(cellphone_people), cellphone_people)
    lstsql = getnerateSQL(config['tblname'], cellphone_people)
    rows = saveToMaria(mydb, lstsql)
    print(rows , ' rows was inserted.')
    mydb.close()



if __name__ == "__main__":
    doit()    
