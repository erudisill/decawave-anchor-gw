import socket
import threading
import SocketServer
import time
from Queue import Queue



class ThreadedTCPRequestHandler(SocketServer.StreamRequestHandler):

    def handle(self):
        # Keep the connection open to stream data
        self.exit_event = threading.Event()
        self.server.addClient(self)
        while self.exit_event.is_set() == False:
            response = self.request.recv(1024);
            # check for broken connection
            if not response:
                break
        self.server.removeClient(self)
            
    def send(self, data):
        try:
            self.wfile.write(data)
            self.wfile.flush()
        except:
            pass

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    
    def __init__(self, address, handler):
        SocketServer.TCPServer.__init__(self, address, handler)
        self._clients = []
        self._data_q = Queue()
        self.exit_event = threading.Event()
        self.data_thread = threading.Thread(target=self._dataLoop)
        self.data_thread.start()
        
    def _dataLoop(self):
        while self.exit_event.is_set() == False:
            while not self._data_q.empty():
                d = self._data_q.get()
                self.broadcast(d)
            time.sleep(0.1)
        
    def addClient(self, client):
        self._clients.append(client)
        
    def removeClient(self, client):
        self._clients.remove(client)
        
    def clientsCount(self):
        return len(self._clients)
    
    def broadcast(self, data):
        for c in self._clients:
            try:
                c.send(data)
            except:
                pass

    def shutdown(self):
        self.exit_event.set()
        for c in self._clients:
            c.exit_event.set()
        SocketServer.TCPServer.shutdown(self)

    def putData(self, data):
        self._data_q.put(data)





def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    while True:
        response = sock.recv(1024)
        if not response: 
            break
        print "Received: " + response
    sock.close()

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    print "Server loop running in thread:", server_thread.name


    client_thread = threading.Thread(target=client,args=(ip,port,"Hello World"))
    client_thread.daemon = True
    client_thread.start()
    
    time.sleep(1)
    server.putData("xxx ")
    time.sleep(1)
    server.putData("yyy ")
    time.sleep(1)
    server.putData("zzz ")
    #client(ip, port, "Hello World 1")
    #client(ip, port, "Hello World 2")
    #client(ip, port, "Hello World 3")

    time.sleep(2)

    server.shutdown()
