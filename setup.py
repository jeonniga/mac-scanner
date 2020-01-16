import os
import json
import cpuinfo
import mysql.connector

def loadConfig(config_file):
    # 설정 파일을 읽는다.
    with open( config_file ) as json_execfile:
        config = json.load(json_execfile)

    return config


def saveToMaria(mydb, sql):
    # mariadb에 설치정보 저장하기
    mycursor = mydb.cursor()
    mycursor.execute(sql)
    mydb.commit()
    print(mycursor.rowcount, "record inserted.")
    return mycursor.rowcount


if __name__ == "__main__":

    config_file = os.getcwd() + '/' + cpuinfo.getCPUiD() + '.json'
    config = loadConfig(config_file)

    try:
        # db접속
        mydb = mysql.connector.connect(
        host=config['dbhost'],
        user=config['dbuser'],
        passwd=config['dbpasswd'],
        database=config['database'],
        port=int(config['dbport'])
        )
        
        phoneno = input('전화번호(숫자만입력해 주세요): ')
        cpuid = cpuinfo.getCPUiD()
        print('본 점포의 장비 번호는 ', cpuid, ' 입니다')

        sql = "insert into customer (phoneno, cpuid) values('{}','{}')".format(phoneno, cpuid)

        saveToMaria(mydb,sql)
    except Exception as e:
        print(e)
    finally:
        mydb.close()
