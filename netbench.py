#Submission Information
#Student Name: Li Hoi Kit
#Student No.: 3035745037
#Development Platform: Windows WSL Ubuntu 20.04
#Python version: 3.8.10


import socket
import sys
import time


#constants
SERVER_PORT_NUMBER = 41023 #Assigned port number range for me: [41200, 41209]
DECIMAL_PLACE = 8 #Round off the floating point numbers to how many decimal places


#Function to be executed when this program is run as a server
def server():
    print("Start as a server node")

    #Create sockets and bind them
    serverTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket
    serverUDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP socket
    serverTCPSocket.bind(("", SERVER_PORT_NUMBER))
    serverUDPSocket.bind(("", SERVER_PORT_NUMBER))

    #Listen and accept client's connection using the TCP socket
    serverTCPSocket.listen()
    print("Server is ready. Listening Address:", serverTCPSocket.getsockname())
    clientTCPSocket, clientTCPAddress = serverTCPSocket.accept()
    print("A client has connected and it is at:", clientTCPAddress)

    # ---------------- Test 1 ----------------

    print("\nStart test1 - large transfer")

    print("From server to client")
    startTime = time.perf_counter()
    testOneSender(clientTCPSocket)
    elapsedTime = (time.perf_counter() - startTime)
    throughPut = (200000000 / elapsedTime) / 1000000 # (Number of Bytes Sent / elapsedTime) / Mb
    print("Elapsed time: " + str(round(elapsedTime, DECIMAL_PLACE)) + " s")
    print("Throughput (from server to client): " + str(round(throughPut, DECIMAL_PLACE)) + " Mb/s")

    print("From client to server")
    testOneReceiver(clientTCPSocket)

    # ---------------- Test 2 ----------------

    print("\nStart test2 - small transfer")

    print("From server to client")
    startTime = time.perf_counter()
    testTwoSender(clientTCPSocket)
    elapsedTime = (time.perf_counter() - startTime)
    throughPut = (10000 / elapsedTime) / 1000000
    print("Elapsed time: " + str(round(elapsedTime, DECIMAL_PLACE)) + " s")
    print("Throughput (from server to client): " + str(round(throughPut, DECIMAL_PLACE)) + " Mb/s")

    print("From client to server")
    testTwoReceiver(clientTCPSocket)

    # ---------------- Test 3 ----------------
    
    print("\nStart test3 - UDP pingpong")

    print("From server to client")
    testThreeSender(serverUDPSocket, clientTCPSocket.getpeername())
    print("From client to server")
    testThreeReceiver(serverUDPSocket, clientTCPSocket.getpeername())


    #close the sockets after finishing everything
    print("End of all benchmarks")
    serverTCPSocket.close()
    serverUDPSocket.close()


#Function to be executed when this program is run as a client
def client(argv) -> None:
    print("Start as a client node")
    serverHostName = argv[1] 

    #create a TCP socket
    clientTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP socket

    #try to connect to the server
    try:
        clientTCPSocket.connect((serverHostName, SERVER_PORT_NUMBER))
    except Exception as e:
        print("Error occured when trying to connecting to the server")
        print(e)
        clientTCPSocket.close()
        sys.exit()

    #create a UDP socket
    clientAddress = clientTCPSocket.getsockname() #Get the current address of the TCP socket
    clientUDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
    clientUDPSocket.bind(clientAddress) #Bind the auto-assigned port number (created during the connect() call of the TCP socket) to the UDP socket
    
    # ---------------- Test 1 ----------------

    print("\nStart test1 - large transfer")
    
    print("From server to client")
    testOneReceiver(clientTCPSocket)

    print("From client to server")
    startTime = time.perf_counter()
    testOneSender(clientTCPSocket)
    elapsedTime = (time.perf_counter() - startTime)
    throughPut = (200000000 / elapsedTime) / 1000000
    print("Elapsed time: " + str(round(elapsedTime, DECIMAL_PLACE)) + " s")
    print("Throughput (from client to server): " + str(round(throughPut, DECIMAL_PLACE)) + " Mb/s")

    # ---------------- Test 2 ----------------

    print("\nStart test2 - small transfer")

    print("From server to client")
    testTwoReceiver(clientTCPSocket)

    print("From client to server")
    startTime = time.perf_counter()
    testTwoSender(clientTCPSocket)
    elapsedTime = (time.perf_counter() - startTime)
    throughPut = (10000 / elapsedTime) / 1000000
    print("Elapsed time: " + str(round(elapsedTime, DECIMAL_PLACE)) + " s")
    print("Throughput (from client to server): " + str(round(throughPut, DECIMAL_PLACE)) + " Mb/s")

    # ---------------- Test 3 ----------------
    
    print("\nStart test3 - UDP pingpong")

    print("From server to client")
    testThreeReceiver(clientUDPSocket, (serverHostName, SERVER_PORT_NUMBER))
    print("From client to server")
    testThreeSender(clientUDPSocket, (serverHostName, SERVER_PORT_NUMBER))

    #close the sockets after finishing everything
    print("End of all benchmarks")
    clientTCPSocket.close()
    clientUDPSocket.close()


def testOneReceiver(tcpSocketObject: socket):
    #Receive until the received buffer size reaches 200000000
    receivedBufferSize = 0
    while receivedBufferSize < 200000000:
        tempBytes = b""
        try:
            remainingBytes = 200000000 - receivedBufferSize
            if (remainingBytes > 10000):
                tempBytes = tcpSocketObject.recv(10000)
            else:
                tempBytes = tcpSocketObject.recv(remainingBytes) #Do not read more than needed

        except Exception as e:
            print("Error occured when trying to receive data in test 1")
            print(e)
            sys.exit()

        #Check and see if the connection is broken with the server
        if tempBytes:
            receivedBufferSize += len(tempBytes) #Accumulate the bytes received
        else:
            print("Connection is broken with the server.")
            sys.exit()

    print("Received total: " + str(receivedBufferSize) + " bytes")

    #Send the 5 bytes to the receiver as acknowledgement
    acknowledgement = bytes(5)
    status = tcpSocketObject.sendall(acknowledgement)
    if(status != None):
        print("Error on sending the acknowledgement in test 1")
        sys.exit()
    

def testOneSender(tcpSocketObject: socket):
    #Send data to server
    #Divide the 200000000 bytes to be sent to 40 parts, so we can show the progress in 40 parts in stdout
    bytesSent = 0 #Keep track of how many bytes has been sent
    for i in range(40):
        #Send 10000 bytes in each call of sendall. Therefore, we need (200000000 / 40) / 10000 = 500 loops
        for i in range(500):
            tempBytes = bytes(10000)
            status = tcpSocketObject.sendall(tempBytes)
            if(status != None): #Failure on sending
                print("Error when trying to send data in test 1")
                sys.exit()
            bytesSent += 10000
        print("*", end=" ") #Finished one of the 40 loops, show progress in stdout
    print("") #Add a newline after the progress bar
    print("Sent total: "+ str(bytesSent) + " bytes")


    #Receive the 5 bytes of small message from the receiver
    receivedSize = 0
    #Keep receiving until 5 bytes has been received
    while receivedSize < 5: 
        try:
            receivedBytes = tcpSocketObject.recv(5 - receivedSize)
            receivedSize += len(receivedBytes)

        except Exception as e:
            print("Error occured when trying to receive acknowledgement in test 1")
            print(e)
            sys.exit()

        #Check and see if the connection is broken with the server
        if receivedBytes:
            #Check if the message is of 5 bytes. If not, it makes no sense, exit.
            if len(receivedBytes) != 5:
                print("Invalid acknowledgement size")
                print(len(receivedBytes))
                sys.exit()
        else:
            print("Connection is broken with the server.")
            sys.exit()


#Logic is similar to test one
def testTwoReceiver(tcpSocketObject: socket):
    receivedBufferSize = 0
    while receivedBufferSize < 10000:
        tempBytes = b""
        try:
            tempBytes = tcpSocketObject.recv(10000 - receivedBufferSize)

        except Exception as e:
            print("Error occured when trying to receive data in test 2")
            print(e)
            sys.exit()
        
        #Check and see if the connection is broken with the server
        if tempBytes:
            receivedBufferSize += len(tempBytes) #Accumulate the bytes received
        else:
            print("Connection is broken with the server.")
            sys.exit()

    print("Received total: " + str(receivedBufferSize) + " bytes")

    #Send the 5 bytes to the receiver as acknowledgement
    acknowledgement = bytes(5)
    status = tcpSocketObject.sendall(acknowledgement)
    if(status != None):
        print("Error on sending the acknowledgement in test 2")
        sys.exit()


#Logic is similar to test one
def testTwoSender(tcpSocketObject: socket):
    #Send data to server
    dummyBytes = bytes(10000)
    status = tcpSocketObject.sendall(dummyBytes)
    if(status != None): #Failure on sending
        print("Error when trying to send data in test 2")
        sys.exit()
    print("Sent total: 10000 bytes")

    #Receive the 5 bytes of small message from the receiver
    receivedSize = 0
    #Keep receiving until 5 bytes has been received
    while receivedSize < 5: 
        try:
            receivedBytes = tcpSocketObject.recv(5 - receivedSize)
            receivedSize += len(receivedBytes)
            
        except Exception as e:
            print("Error occured when trying to receive acknowledgement in test 2")
            print(e)
            sys.exit()

        #Check and see if the connection is broken with the server
        if receivedBytes:
            #Check if the message is of 5 bytes. If not, it makes no sense, exit.
            if len(receivedBytes) != 5:
                print("Invalid acknowledgement size")
                print(len(receivedBytes))
                sys.exit()
        else:
            print("Connection is broken with the server.")
            sys.exit()


def testThreeReceiver(udpSocketObject: socket, address: (str, int)):
    for i in range(5):
        receivedBytes = udpSocketObject.recvfrom(100)
        if(len(receivedBytes[0]) != 5):
            print("size of received bytes makes no sense!")
            sys.exit()
        udpSocketObject.sendto(receivedBytes[0], address) #pong!

        print('*', end=" ") #print one * for each successful PONG
    print("") #newline after printing the whole progress bar


def testThreeSender(udpSocketObject: socket, address: (str, int)):
    total = 0 #Records the total time spent on the five ping-pongs
    dummyBytes = bytes(5) #dummy bytes to be sent

    for i in range(5):
        startTime = time.perf_counter()

        udpSocketObject.sendto(dummyBytes, address)
        receivedBytes = udpSocketObject.recvfrom(100) #ping!
        if(len(receivedBytes[0]) != 5): #Check if the size of received bytes make sense
            print("size of received bytes makes no sense!")
            sys.exit()
        
        rtt = time.perf_counter() - startTime
        total += rtt
        print("Reply from " + address[0] + ": time = " + str(round(rtt, DECIMAL_PLACE)) + " s")

    print("Average RTT: " + str(round(total/5, DECIMAL_PLACE)) + " s")

        
if __name__ == '__main__':
    argumentLength = len(sys.argv)
    if argumentLength > 2:
        print("Usage: ./netbench.py <hostname of server>(optional)")
    elif argumentLength == 2: #Two arguments. Run the program as a client
        client(sys.argv)
    else: #One argument only. Run the program as a server
        server()
