from urlparse import urlparse
from threading import Thread
import httplib, sys, time
from Queue import Queue

total_conn = 5000
concurrent = 1000
q = Queue(total_conn)

success = 0
cnt_error = 0

def doWork(seq):
    try:
        while True:
            url = q.get()
            status, url = getStatus(url)
            doSomethingWithResult(status, url)
            q.task_done()
    except Exception, e:
        print seq, e

def getStatus(ourl):
    global success
    global cnt_error
    try:
        url = urlparse(ourl)
        conn = httplib.HTTPConnection(url.netloc)   
        conn.request("HEAD", url.path)
        res = conn.getresponse()
        conn.close()
        success = success + 1
        return res.status, ourl
    except:
        cnt_error = cnt_error + 1
        return "error", ourl
        if conn is not None: conn.close()

def doSomethingWithResult(status, url):
    print status, url

def main():
    ts = time.time()
    
    for i in range(concurrent):
        t = Thread(target=doWork, kwargs={'seq': i})
        t.daemon = True
        t.start()
        
    try:
        url_list = []
        # read from file and append to a file
        for url in open('urllist.txt'):
            url_list.append(url)
        
        # for each url_list add a url to queue
        count = 0
        while True:
            if count > total_conn: break
            
            for url in url_list:
                q.put(url.strip())
                count += 1
        q.join()
    except KeyboardInterrupt:
        sys.exit(1)
        
    dur=time.time() - ts
    print('Took {}'.format(dur))
    
    print "total= %d success= %d error= %d" % (concurrent, success, cnt_error)
    print "connections per second= %.2f cps" % (success/dur)
    
    
    
    
main()
    

