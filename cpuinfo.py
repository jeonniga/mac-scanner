import os
import subprocess
from datetime import datetime

def blockexec(cmd):
    # 프로세스를 실행하고 stdout, stderr를 리턴
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    out, err = proc.communicate()

    if out!=None:
        out = out.decode('utf-8')
    else:
        out = ''

    if err!=None:
        err = err.decode('uft-8')
    else:
        err = ''

    return out.replace('\n',''), err.replace('\n','')


def cpu_info():
    # cpu id를 얻고 출력과 에러메시지를 각각 담아 리턴
    stdout, stderr = blockexec("cat /proc/cpuinfo | grep Serial | awk '{print $3}'")
    return stdout, stderr


def getFile(ext='.html'):
    # cpu id를 기반으로 파일이름을 얻는다 CPUID_연월일시분초.ext 형식, 기본값 .html
    cpuinfo, _ = cpu_info()
    print("CPU ID  : %s" % cpuinfo)
    datestr = "{:%Y%m%d%H%M%S}".format(datetime.now())
    return cpuinfo + "_" + datestr + ext



def getCPUiD():
    # cpu id를 얻는다 
    cpuinfo, _ = cpu_info()
    print("CPU ID  : %s" % cpuinfo)
    return cpuinfo



def getDateTimestr():
    # 현재의 연월일시분초를 문자열 타입으로 받는다
    datestr = "{:%Y%m%d%H%M%S}".format(datetime.now())
    return datestr

def getDateTime():
    # 현재의 연월일시분초를 에포크 타임으로 받는다
    return datetime.now()