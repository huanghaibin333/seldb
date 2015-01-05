from sqlalchemy import Column, Sequence, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import subprocess
import time, sched

def read_sensor():
    temp = []
    sensor = {}
    p = subprocess.Popen('ipmitool -I lan -H 116.57.78.28 -U ADMIN -P ADMIN sensor list', stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    stdoutdata = p.communicate()
    try:
        data = stdoutdata[0].strip(None).split('\n')
        for line in data:
                info = [str.strip() for str in line.split('|')]
                temp.append(info)
    
    except AttributeError:
        pass
    
    sensor['cpu1 temp'] = temp[0][1]
    sensor['cpu2 temp'] = temp[1][1]
    sensor['system temp'] = temp[2][1]
    sensor['peripheral temp'] = temp[3][1]
    sensor['fan1 rpm'] = temp[5][1]
    sensor['fan5 rpm'] = temp[9][1]
    
    return sensor

def sel_filter(id=''):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sel = session.query(Sel).filter(Sel.id==id, )
    return sel