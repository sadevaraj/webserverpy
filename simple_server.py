import socket
import threading
import select
import sys

HttpOkStr = "HTTP/1.1 200 Okay\r\n"
HttpHeaderStr = "Content-Type: text/html; charset=ISO-8859-4 \r\n\r\n"
LoginPage = [HttpOkStr,
             HttpHeaderStr,
             "<head>Login</head><body><form action='http://localhost:8888' method='post'>",
             "username   ",
             "<input type='text' name='username'></br>",
             "password   ",
             "<input type='text' name='password'></br>",
             "<input type='submit' value='Login'>",
             "</form></body>"]
ResponsePageHead = [HttpOkStr,
                    HttpHeaderStr,
                    "<title>Login Response</title>",
                    "<body>"]
ResponseTailStr = "</body>"
  
class ClientHandle(threading.Thread):
    """ Sends login page to clients for HTTP GET request, Sends validated response for HTTP POST request """
    def __init__(self, aConnection):
        threading.Thread.__init__(self)
        self.iConnection = aConnection
        self.iSize = 1024
        self.iKeyValDict = {"username":"","password":""}
        
    def validate(self):
        if(self.iKeyValDict["username"] == "user@example.com" and self.iKeyValDict["password"] == "password"):
            return True
        else:
            return False
        
    def fetchFormData(self, aResponse):
        dataStr = aResponse.split("\r\n\r\n")[1]
        for elements in dataStr.split("&"):
            pairs = elements.split("=")
            self.iKeyValDict[pairs[0]] = pairs[1].replace("%40","@")     
    
    def run(self):
        response = self.iConnection.recv(self.iSize)
        strGET = response.split("\n",2)[0]
        if(strGET.find("GET / HTTP/") != -1):
            self.iConnection.send(''.join(LoginPage))           
        elif(strGET.find("POST / HTTP/") != -1):
            self.iConnection.send("".join(ResponsePageHead))
            self.fetchFormData(response)
            self.iConnection.send("welcome" if (self.validate()) else "Login Failed")
            self.iConnection.send(ResponseTailStr)
        else:
            print "Not HTTP GET or POST request doNothing!" 
        self.iConnection.close()
  
        
class SimpleServer:
    """ creates server socket, listens to local port 8888 and starts a thread to handle connections """
    def __init__(self):
        self.iHOST = 'localhost'
        self.iPORT = 8888
        self.iServerSoc = None
        self.iThreadList = []
             
    def openSocket(self):
        try:
            self.iServerSoc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.iServerSoc.bind((self.iHOST,self.iPORT))
            self.iServerSoc.listen(5) 
        except socket.error, message:
            if self.iServerSoc:
                self.iServerSoc.close()
            sys.stderr.write("ERROR :%s" % message[1])
            sys.exit(1)
        
    def startServer(self):
        print "simple server starting..."
        self.openSocket()
        inputList = [self.iServerSoc,sys.stdin]
        loop = True
        print "Listening for client request from local port 8888... "
        print "Press Enter to stop server"
        while (loop):
            ip = select.select(inputList, [], [])
            for elements in ip[0]:
                if elements == self.iServerSoc:
                    handleConnections = ClientHandle(self.iServerSoc.accept()[0])
                    handleConnections.start()
                    self.iThreadList.append(handleConnections)
                elif elements == sys.stdin:
                    sys.stdin.readline()
                    loop = False       
                    print "simple server stopped ..."
        self.iServerSoc.close()
        for threadElements in self.iThreadList:
            threadElements.join()
   
if __name__ == "__main__":
    objServer = SimpleServer()
    objServer.startServer()
    
    
