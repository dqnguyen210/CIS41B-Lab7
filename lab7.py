#lab 7: Write a program that measures the data transfer speed between threads and between processes. 
#       Then write a conclusion based on the resulting program output. 
#Name: Quynh Nguyen
#Date: 3/5/18

'''
2 queues are used to send data back and forth between parent and child because with one queue, 
only the parent can use the data. It put data in and get the same data that it put in after that.
'''
'''
One queue requires more work in synchronizing the parent and child. One way to solve is using event.
Need to synchronizing because the 2 processes are not guaranteed to work one after another.
'''
import multiprocessing as mp
import time
import pickle
import socket
import threading
import queue
import platform

HOST = '127.0.0.1'
PORT = 4565
LISTFLAG = 1

def incrementQueue(fromMain, fromChild, listFlag=0) :
    data = fromMain.get()
    if listFlag:
        while data != [] :
            fromChild.put(data + [1])
            data = fromMain.get()        
    else :
        while data != 0 :
            fromChild.put(data+1)
            data = fromMain.get()

def threadWithQueue(listFlag = 0) :
    fromMain = queue.Queue()
    fromChild = queue.Queue()    
    thread = threading.Thread(target=incrementQueue, args=(fromMain, fromChild, listFlag))
    
    loopCount = 1000
    data = 0
    if listFlag:
        loopCount = 300
        data = []     
        
    thread.start()      
    start = time.time()
    for i in range(loopCount):
        fromMain.put(data+ [0]) if listFlag else fromMain.put(data+1)
        data = fromChild.get()
    end = time.time()
    fromMain.put([]) if listFlag else fromMain.put(0)
    thread.join()
    validateData(data, loopCount, listFlag)
    return (loopCount*2)/(end-start)
    
    
def processWithQueue(listFlag = 0) :
    fromMain = mp.Queue()
    fromChild = mp.Queue()    
    process = mp.Process(target=incrementQueue, args=(fromMain, fromChild, listFlag))
    
    loopCount = 1000
    data = 0
    if listFlag:
        loopCount = 300
        data = []        
    process.start()      
    start = time.time()
    for i in range(loopCount):
        fromMain.put(data+ [0]) if listFlag else fromMain.put(data+1)
        data = fromChild.get()
    end = time.time()
    fromMain.put([]) if listFlag else fromMain.put(0)
    process.join()
    validateData(data, loopCount, listFlag)
    return (loopCount*2)/(end-start)

def incrementSocket(listFlag) : #server
    with socket.socket() as s : #open socket
        s.bind((HOST, PORT))    #make socket available at the PORT number
                                #and with HOST name
    
        s.listen()      #activate listener at the port
        (conn, addr) = s.accept()  
                
        while True:
            data = pickle.loads(conn.recv(2048))
            if data == [] if listFlag else data == 0:
                break
            conn.send(pickle.dumps(data+[1])) if listFlag else conn.send(pickle.dumps(data+1))
    
    
def threadWithSocket(listFlag=0) : #client
    thread = threading.Thread(target=incrementSocket, args=(listFlag,))
    thread.start()
    data = 0
    loopCount = 1000
    if listFlag:
        data = []
        loopCount = 300        
    with socket.socket() as s : #open socket
        s.connect((HOST, PORT)) #connect to server w/ 2 IDs: hostname and port number
                                #connect is blocking
        start = time.time()        
        for i in range(loopCount):
            s.send(pickle.dumps(data+[0])) if listFlag else s.send(pickle.dumps(data+1))            
            data = pickle.loads(s.recv(2048))
        end = time.time()
        s.send(pickle.dumps([])) if listFlag else s.send(pickle.dumps(0))
        thread.join()
        validateData(data, loopCount, listFlag)
        return (loopCount*2)/(end-start)        

def processWithSocket(listFlag=0) :  #client
    process = mp.Process(target=incrementSocket, args=(listFlag,))
    process.start()
    data = 0
    loopCount = 1000
    if listFlag:
        data = []
        loopCount = 300        
    with socket.socket() as s : #open socket
        s.connect((HOST, PORT)) #connect to server w/ 2 IDs: hostname and port number
                                #connect is blocking
        start = time.time()        
        for i in range(loopCount):
            s.send(pickle.dumps(data+[0])) if listFlag else s.send(pickle.dumps(data+1))            
            data = pickle.loads(s.recv(2048))
        end = time.time()
        s.send(pickle.dumps([])) if listFlag else s.send(pickle.dumps(0))
        process.join()
        validateData(data, loopCount, listFlag)
        return (loopCount*2)/(end-start)  
    
def validateData(data, loopCount, listFlag) :
    if data != [i%2 for i in range(loopCount*2)] if listFlag else data != loopCount*2 :
        raise ValueError("=> Data value is not as expected")
    
def main():
    try :
        print("OS:", platform.system())
        print("Processor:", platform.processor())
        print("Num of cores: %d" %mp.cpu_count())
        print("\t\t Thread    Process")
        print("%-7s %-9s %-9d %d" %('Queue', 'Integer', threadWithQueue(), processWithQueue()))
        print("%-7s %-9s %-9d %d" %('Queue', 'List', threadWithQueue(LISTFLAG), processWithQueue(LISTFLAG)))
        print("%-7s %-9s %-9d %d" %('Socket', 'Integer', threadWithSocket(), processWithSocket()))
        print("%-7s %-9s %-9d %d" %('Socket', 'List', threadWithSocket(LISTFLAG), processWithSocket(LISTFLAG)))

    except ValueError as e:
        print(str(e))
        raise SystemExit
        
if __name__ == '__main__' :
    main()

'''
From the output, I see that using processes with queues to transfter data is the least efficient way.
It is 5-6 times slower than using other methods. Threads with queues is the fastest way (around 40,000-50,000 
data transferred per second). With socket, threads and processes yield approximately the same amount of data
transferred. In general, a small data size like integer is easier to transfer than a larger data size like list.
More than twice the integer data was transferred compared to list data when using threads with socket and processes with 
sockets or queues. Therefore, the best way to transfer large data size is to use threads with queues.
 => Threads are faster than procecsses when it comes to data transfer
'''