#!/usr/bin/env python
# -*- coding: utf-8 -*-

# File name: test_.py
# Author: Haibin Huang
# Version: 1.0
# Create Date: 2014/12/3

import os, time, random
from multiprocessing import Process
from multiprocessing import Pool

def fork_():
    print 'Process %s start...' % os.getpid()
    pid =  os.fork()
    
    if pid == 0:
        print 'I am child process %s and my parent is %s' % (os.getpid(), os.getppid())
    else:
        print 'I am parent process %s and my child process is %s' % (os.getpid(), pid)

def run_proc(name):
    print 'Run process %s ' % name
    start = time.time()
    time.sleep(random.random() * 4)
    end = time.time()
    print "Process %s runs %0.2f" %(name, (end-start))
    
        
def process_():
    print 'Parent process %s ' % os.getgid()
    p = Process(target=run_proc, args=('child',))
    print 'new process will start'
    p.start()
    p.join()
    print 'All process are done'
    
def pool_():
    print 'Parent process %s' % os.getpid()
    p = Pool()
    for i in range(5):
        p.apply_async(run_proc, args=(i,))
    print 'Waiting all process done'
    p.close()
    p.join()
    print 'All processes done'
 
if __name__ == '__main__':
    fork_()
    run_proc('h')
    process_()
    pool_()
        


    