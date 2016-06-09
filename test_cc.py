from urlparse import urlparse
from threading import Thread, Lock
import httplib, sys, time
from Queue import Queue

total_conn = 5000
concurrent = 10
q = Queue(total_conn)

success = 0
cnt_error = 0
done = 0
prev_done = 0

slock = Lock()
def count_success():
    global success
    slock.acquire()
    try:
      success = success + 1
    except Exception, e:
        print seq, e
    finally:
        slock.release()

elock = Lock()
def count_error():
    global cnt_error
    elock.acquire()
    try:
      cnt_error = cnt_error + 1
    except Exception, e:
        print seq, e
    finally:
        elock.release()

dlock = Lock()
def count_done():
    global done
    dlock.acquire()
    try:
      done = done + 1
    except Exception, e:
        print seq, e
    finally:
        dlock.release()

def checkWork():
    global prev_done
    try:
        while done < total_conn:
            print "DONE= %6d SUCCESS= %6d ERROR= %6d DIFF= %6d" % (done, success, cnt_error, done - prev_done)
            prev_done = done
            time.sleep(1)
    except Exception, e:
        print e

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
    try:
        url = urlparse(ourl)
        conn = httplib.HTTPConnection(url.netloc)   
        conn.request("HEAD", url.path)
        res = conn.getresponse()
        count_success()
        conn.close()
        return res.status, ourl
    except:
        count_error()
        if conn is not None: conn.close()
        return "error", ourl


def doSomethingWithResult(status, url):
    count_done()
    #print status, url

def main():
    ts = time.time()

    print "==========================================================================="
    print " TOTAL REQ= %d NUM_WORKERS= %d" % (total_conn, concurrent)
    print "==========================================================================="
    
    for i in range(concurrent):
        t = Thread(target=doWork, kwargs={'seq': i})
        t.daemon = True
        t.start()
        
    try:
        url_list = []
        # read from file and append to a file
        for url in open('urllist.txt'):
            url_list.append(url)
        
        p = Thread(target=checkWork)
        p.daemon = True
        p.start()

        # for each url_list add a url to queue
        count = 0
        while True:
            if count >= total_conn: break
            
            for url in url_list:
                q.put(url.strip())
                count += 1
        q.join()
    except KeyboardInterrupt:
        sys.exit(1)
        
    print "==========================================================================="
    dur=time.time() - ts
    print(' Took {}'.format(dur))
    
    print " TOTAL= %d success= %d error= %d" % (total_conn, success, cnt_error)
    print " CPS= %.2f cps" % (success/dur)
    print "==========================================================================="
    
main()
    

