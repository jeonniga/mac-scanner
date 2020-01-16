"""
     subprocess의 Popen을 이용해 프로세스를 실행하는 기능
"""
import os
import subprocess

def blockexec(cmd):
    # 프로세스를 실행하고 stdout, stderr를 리턴
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setsid)
    
    out, err = proc.communicate()
    if out!=None:
        out = out.decode('utf-8')
    else:
        out = ''

    if err!=None:
        err = err.decode('utf-8')
    else:
        err = ''

    return out, err

def nonblockexec(cmd):
    # 프로세스를 실행하고 pid를 리턴받음
    proc = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
    return proc.pid