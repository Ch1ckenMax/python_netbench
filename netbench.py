#Submission Information
#Student Name: Li Hoi Kit
#Student No.: 3035745037
#Development Platform: Windows WSL Ubuntu 20.04
#Python version: 3.8.10

import socket
import sys
import time

#constants
SERVER_PORT_NUMBER = 41022 #Assigned port number range for me: [41200, 41209]

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

    #close the sockets after finishing everything
    serverTCPSocket.close()
    serverUDPSocket.close()



#Function to be executed when this program is run as a client
def client(argv):
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

    #close the sockets after finishing everything
    clientTCPSocket.close()
    clientUDPSocket.close()




if __name__ == '__main__':
    argumentLength = len(sys.argv)
    if argumentLength > 2:
        print("Usage: ./netbench.py <hostname of server>(optional)")
    elif argumentLength == 2: #Two arguments. Run the program as a client
        client(sys.argv)
    else: #One argument only. Run the program as a server
        server()
