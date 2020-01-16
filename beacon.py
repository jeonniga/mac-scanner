"""
    pip install daemon
    pip install python-daemon
"""

import os
import cpuinfo
import scanner
import _thread
import time

import ftplib
import cpuinfo


def mon(config):
    """
        모니터링 실시
    """
    while True:
        try:
            scanner.doit()
        except KeyboardInterrupt:
            break

        time.sleep(int(config['capture_interval']))


def getConfig(config):
    while True:
        try:
            ftp = ftplib.FTP()
            ftp.connect(config["ftphost"],config["ftpport"])
            ftp.login(config["ftpid"],config["ftppw"])
            ftp.cwd(config["ftpdir"])
            filenames = [cpuinfo.getCPUiD()+".json", "cellphon.json", "pmanager.json", "exec.json"]
            for filename in filenames:
                fd = open("./" + filename, 'wb')
                ftp.retrbinary("RETR " + filename, fd.write)
            fd.close()
        except Exception as e:
            print(e)
        
        time.sleep(3600)

if __name__ == "__main__":
    # 설정 파일 정보 로드
    config_file = os.getcwd() + '/' + cpuinfo.getCPUiD() + '.json'
    config, phonedb = scanner.loadConfig(config_file)

    # 모니터링 실시를 위한 쓰레드
    _thread.start_new_thread(mon, (config, ))
    # 설정 파일들 갱신을 위한 쓰레드
    _thread.start_new_thread(getConfig, (config, ))

    while True:
        time.sleep(30)
