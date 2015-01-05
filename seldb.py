#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File name: seldb.py
# Author: Haibin Huang
# Version: 1.0
# Create Date: 2014/12/3

from sqlalchemy import Column, Sequence, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
import subprocess
import time, sched


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(40))
    password = Column(String(40))
    ip = Column(String(40))

class Sel(Base):
    __tablename__ = 'sel'
    id = Column(Integer, Sequence('sel_id_seq'), primary_key=True)
    date = Column(String(40))
    time = Column(String(40))
    event = Column(String(40))
    state = Column(String(40))
    action = Column(String(40))
    detail = relationship('Detail')

class Detail(Base):
    __tablename__ = 'detail'
    id = Column(Integer, Sequence('detail_id_seq'), primary_key=True)
    sel_id = Column(Integer, ForeignKey('sel.id'))
#    sel = relationship('Sel', backref=backref('detail', order_by=id))
    record_type = Column(String(4))
    timestamp = Column(String(40))
    generator_id = Column(String(4))
    evm_revision = Column(String(4))
    sensor_type = Column(String(40))
    sensor_num = Column(String(4))
    event_type = Column(String(40))
    event_direction = Column(String(40))
    event_data = Column(String(40))
    event_inter = Column(String(40))
    description = Column(String(60))
    sensor_id =  Column(String(40))
    entity_id =  Column(String(40))
    discrete =  Column(String(40))
    states_asserted =  Column(String(40))

#初始化数据库连接
engine = create_engine('mysql+mysqlconnector://root:123@localhost:3306/sel')
#创建数据表
Base.metadata.create_all(engine)
#创建DBSession类型

def user_add(name, password, ip):
    user = User(name=name, password=password, ip=ip)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add(user)
    session.commit()
    session.close()

def sel_add(date, time, event, state, action, record_type='', timestamp='', generator_id='', evm_revision='', sensor_type='', sensor_num='', event_type='',event_direction='',\
            event_data='', event_inter='', description='', sensor_id='',entity_id='', discrete='', states_asserted=''):
    sel = Sel(date=date, time=time, event=event, state=state, action=action)
    sel.detail = [Detail(record_type=record_type,\
                        timestamp=timestamp,\
                        generator_id=generator_id,\
                        evm_revision=evm_revision,\
                        sensor_type=sensor_type,\
                        sensor_num=sensor_num,\
                        event_type=event_type,\
                        event_direction=event_direction,\
                        event_data=event_data,\
                        event_inter=event_inter,\
                        description=description,\
                        sensor_id=sensor_id,\
                        entity_id=entity_id,\
                        discrete=discrete,\
                        states_asserted=states_asserted)]
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add(sel)
    session.commit()
    session.close()

def read_sel():
    'Get sel information form remote server, and return data by list'
    sel = []
    p = subprocess.Popen('ipmitool -I lan -H 116.57.78.28 -U ADMIN -P ADMIN sel list', stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    stdoutdata = p.communicate()
    try:
        data = stdoutdata[0].strip(None).split('\n')
        for line in data:
            info = [str.strip() for str in line.split('|')]
            sel.append(info)
    except AttributeError:
        pass
    return sel

def read_detail(sel_id):
    'Get sel detail information form remote server, and return data by dict'
    sel_detail={}
    time.sleep(2)
    model = {'SEL Record ID':'sel_id', 'Record Type': 'record_type',\
             'Timestamp':'timestamp', 'Generator ID':'generator_id',\
             'EvM Revision':'evm_revision', 'Sensor Type':'sensor_type',\
             'Sensor Number':'sensor_num', 'Event Type':'event_type',\
             'Event Direction':'event_direction', 'Event Data':'event_data',\
             'Event Interpretation':'event_inter', 'Description':'description',\
             'Sensor ID':'sensor_id', 'Entity ID':'entity id',\
             'Sensor Type(Discrete)':'discrete', 'States Asserted':'states_asserted'}
    cmd = 'ipmitool -I lan -H 116.57.78.28 -U ADMIN -P ADMIN sel get ' + sel_id
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, universal_newlines=True)
    stdoutdata = p.communicate()
    try:
        data = stdoutdata[0].strip(None).split('\n')
        for line in data:
            dic = line.split(':')
            sel_detail[model[dic[0].strip()]]=dic[1].strip()
    except :
        pass
    
    if sel_detail.get('sel_id'):
        del sel_detail['sel_id']
    
    return sel_detail

def update_sel():
    sel = read_sel()
    Flag = 1
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    try:
        date = session.query(Sel)[-1].date
        time = session.query(Sel)[-1].time
        for line in sel:
            if  line[2]!=time or line[1]!= date:
                Flag += 1
            else:
                break
    except IndexError:
        Flag = 1
    finally:
        session.close()
    if Flag ==1:
        for i in range(Flag, len(sel)+1):
            sel_detail = read_detail(str(i))
            sel_add(date=sel[i-1][1], time=sel[i-1][2], event=sel[i-1][3], state=sel[i-1][4], action=sel[i-1][5], **sel_detail)
    elif Flag != len(sel):
        for i in range(Flag, len(sel)):
            sel_detail = read_detail(str(i+1))
            sel_add(date=sel[i][1], time=sel[i][2], event=sel[i][3], state=sel[i][4], action=sel[i][5], **sel_detail)

#初始化sched模块的scheduler类
#第一个参数是一个可以返回时间戳的函数，第二个参数可以在定时未到达之前阻塞。
s = sched.scheduler(time.time,time.sleep)

#enter四个参数分别为：间隔事件、优先级（用于同时间到达的两个事件同时执行时定序）、被调用触发的函数，给他的参数（注意：一定要以tuple给如，如果只有一个参数就(xx,)）
def perform(interval):
    s.enter(interval,0,perform,(interval,))
    update_sel()

def update_period(interval=4):
    s.enter(0,0,perform,(interval,))
    s.run()

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

if __name__ == "__main__":
    update_period(10)