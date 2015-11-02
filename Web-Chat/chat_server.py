#
# tcpchatserver_nonblocking.py
# TCP/IP Chat server
# The server accepts connection from multiple clients and
# broadcasts data sent by a client to all other clients
# which are online (connection active with server)
#

import socket
import select
import string
import thread
import sys, time
import traceback

def broadcast_data (sock, message):
    """Send broadcast message to all clients other than the
       server socket and the client socket from which the data is received."""

    global CONNECTIONS
    
    for socket in CONNECTIONS:
        if socket != sock:            
            socket.send(message)

def accept_connection():

    global CONNECTIONS, RECV_BUFFER

    try:

        while 1:

            threadlock.acquire()

            try:

                #print "waiting for accept"
                sockfd, addr = server_socket.accept()
                # Set socket to non-blocking mode
                sockfd.setblocking(0)
                CONNECTIONS.append(sockfd)
                print ("Client (%s, %s) connected" % addr)
                broadcast_data(sockfd, "Client (%s, %s) connected" % addr)

            except:
                pass

            threadlock.release()

    except:
        #Handle the case when client program is terminated with Ctrl-C
        #catch the exception and exit
        pass

def process_connection():

    global CONNECTIONS, RECV_BUFFER

    try:

        while 1:

            #print "waiting for packet"
            for sock in CONNECTIONS:

                threadlock.acquire()

                try:

                    data = sock.recv(RECV_BUFFER)

                    if data:

                        # The client sends some valid data, process it

                        if data == "/logout":

                            broadcast_data(sock, "Client (%s, %s) quits" % sock.getpeername())
                            print "Client (%s, %s) quits" % sock.getpeername()
                            sock.close()
                            CONNECTIONS.remove(sock)

                        else:

                            broadcast_data(sock, data)

                except:

                    #Exception thrown, get the error code and do cleanup actions
                    socket_errorcode =  sys.exc_value[0]

                    if socket_errorcode == 10054:

                        # Connection reset by peer exception
                        # In Windows, sometimes when a TCP client program closes abruptly,
                        # or when you press Ctrl-C a "Connection reset by peer" exception will be thrown

                        broadcast_data(sock, "Client (%s, %s) quits" % sock.getpeername())
                        print "Client (%s, %s) quits" % sock.getpeername()
                        sock.close()
                        CONNECTIONS.remove(sock)

                    else:
                        # The socket is not ready for reading, which results in an exception,
                        # ignore this and pass on with the next client socket (without blocking)
                        # The exception you will see here is
                        # "The socket operation could not complete without blocking"
                        pass

                threadlock.release()

    except:
        #Handle the case when server program is terminated with Ctrl-C
        #catch the exception and exit
        pass
               
if __name__ == "__main__":

    CONNECTIONS=[]
    RECV_BUFFER=4096

    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 50116))
    server_socket.listen(10)
    server_socket.setblocking(0)

    threadlock = thread.allocate_lock()

    print ("Chat Server started")
    
    thread.start_new_thread(accept_connection, ())
    thread.start_new_thread(process_connection, ())

    try:
        while 1:
            pass
    except:
        server_socket.close()
