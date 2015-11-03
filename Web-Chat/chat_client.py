#
# tcpchatclient_nonblocking.py
# TCP/IP Chat client
# The client program connects to server and sends data to other connected 
# clients through the server
#

import socket
import thread
import sys


HOST = '127.0.0.1'    # The remote host
PORT = 50116           # The same port as used by the server
RECV_BUFFER=4096
username = raw_input("Enter a user name:")


def recv_data():
    "Receive data from other clients connected to server"
    while 1:
        try:
            recv_data = client_socket.recv(RECV_BUFFER)            
        except:
            #Handle the case when server process terminates
            print "Server closed connection, thread exiting."
            thread.interrupt_main()
            break
        if not recv_data:
                # Recv with no data, server closed connection
                print "Server closed connection, thread exiting."
                thread.interrupt_main()
                break
        else:
                print recv_data

def send_data():
    "Send data from other clients connected to server"
    global username
    while 1:
        send_data = str(raw_input(username + ": "))
        data_list = send_data.split(" ", 2)
        if send_data == "/logout":
            client_socket.send(send_data)
            thread.interrupt_main()
            break
        elif len(data_list) >= 3:
            if data_list[1] == "username":
              username = data_list[2]
              client_socket.send(send_data)
            else:
                client_socket.send(send_data)
        else:
            client_socket.send(send_data)
        
if __name__ == "__main__":

    print "*******TCP/IP Chat client program********"
    print "Connecting to server at %s:%s" % (HOST, PORT)
    print "Enter a message with the Enter key. To quit, type \"/logout\""

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    client_socket.send("/set username " + username)

    print "Connected to server at %s:%s" % (HOST, PORT)

    thread.start_new_thread(recv_data,())
    thread.start_new_thread(send_data,())

    try:
        while 1:
            continue
    except:
        print "Client program quits...."
        client_socket.close()
        
    
    


