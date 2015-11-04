import socket
import select
import string
import thread
import sys, time
import traceback
from Connection import Connection

def broadcast (connection, message):
    """Send broadcast message to all clients other than the
       server socket and the client socket from which the data is received."""

    global CONNECTIONS
    for c in CONNECTIONS:
        if c not in connection.ignore_list and connection not in c.ignore_list:
            c.sock.send(message)

def accept_connection():

    global CONNECTIONS, RECV_BUFFER

    try:

        while 1:

            threadlock.acquire()

            try:

                sockfd, addr = server_socket.accept()
                con = Connection(sockfd)
                CONNECTIONS.append(con)
                # Set socket to non-blocking mode
                con.sock.setblocking(0)
                print "Client (%s, %s) connected" % addr
                broadcast(con, "Client (%s, %s) connected" % addr)

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

            for c in CONNECTIONS:

                threadlock.acquire()

                try:

                    data = c.sock.recv(RECV_BUFFER)

                    if data:
                        
                        #Checks if user typed "/logout" and kicks them if they did
                        if data == "/logout":
                            if c.username != "":
                                broadcast(c, c.username + " logged out")
                            else:
                                broadcast(c, "Client (%s, %s) quits" % c.sock.getpeername())
                            print "Client (%s, %s) quits" % c.sock.getpeername()
                            c.sock.close()
                            CONNECTIONS.remove(c)

                        #Check is username has been set yet. If not, sets username (assuming data is valid)
                        if c.username == "" and data[0] != "/":
                            found = False
                            for con in CONNECTIONS:
                                if con.username == data:
                                    c.sock.send("Username already taken")
                                    found = True
                                    break

                            if found ==  False:
                                broadcast(c, data + " logged in")
                                c.username = data;
                        elif c.username == "":
                            c.sock.send("Invalid username. Please try again")
         
                        #Process data. If it is a command (starts with "/"), process it. Otherwise broadcast message
                        elif data[0] == "/":

                            data_list = data.split(" ", 1)
                            if data_list[0] == "/set":
                                #not necessary but decided to make it less ambigious
                                data_list = data.split(" ", 2)
                                if data_list[1] == "username" and data_list[2] != "":
                                    found = False
                                    for con in CONNECTIONS:
                                        if con != c.sock:
                                          if con.username == data_list[2]:
                                            c.sock.send("Username already taken")
                                            found = True
                                            break

                                    if found ==  False and data_list[2][0] != "/":
                                        broadcast(c, "User "+ c.username + " assumes new handle " + data_list[2])
                                        c.username = data_list[2]

                                    else:
                                        c.sock.send("Invalid username")

                                else:
                                    c.sock.send("Invalid command")

                            
                            #Blocks users by finding their connection object by username and adding it to the blocker's ignore_list
                            elif data_list[0] == "/block":
                                if data_list[1] != "":
                                    found = False
                                    for e in CONNECTIONS:
                                        if e.username == data_list[1] and c != e and e not in c.ignore_list:
                                            c.ignore_list.append(e)
                                            found = True
                                            break
                                        
                                    if found:
                                        c.sock.send("User " + data_list[1] + " successfully blocked")
                                    else:
                                        c.sock.send("User " + data_list[1] + " not found")
                                else:
                                    c.sock.send("Invalid command")
                            
                            #Works just like blocking users except removes their connection object from the ignore_list
                            elif data_list[0] == "/unblock":
                                if data_list[1] != "":
                                    found = False
                                    for e in CONNECTIONS:
                                        if e.username == data_list[1] and c != e and e in c.ignore_list:
                                            c.ignore_list.remove(e)
                                            found = True
                                            break
                                        
                                    if found:
                                        c.sock.send("User " + data_list[1] + " is no longer being blocked")
                                    else:
                                        c.sock.send("User " + data_list[1] + " not found")
                                else:
                                    c.sock.send("Invalid command")

                            #Checks connections and sends any users online who aren't blocked
                            elif data_list[0] == "/view":
                                c.sock.send("Users online: ")
                                first = False
                                for e in CONNECTIONS:
                                    if e.sock != c.sock and e not in c.ignore_list and c not in e.ignore_list:
                                        if first == False:
                                            c.sock.send(e.username)
                                            first = True
                                        else:
                                            c.sock.send("\n" + e.username)
                            


                            elif data == "/help":
                                c.sock.send("The following commands are:\n/view: View all available users in the chatroom\n/block [username]: Put the user on your ignore list"
                                            +"\n/unblock: Remove the user from your ignore list\n/logout: Sign out of chat\n/help: View the help menu")
                            
                            else:
                                c.sock.send("Invalid command")

                        else: 
                            broadcast(c, c.username + ": " + data)


                except:

                    #Exception thrown, get the error code and do cleanup actions
                    socket_errorcode =  sys.exc_value[0]

                    if socket_errorcode == 10054:

                        # Connection reset by peer exception
                        # In Windows, sometimes when a TCP client program closes abruptly,
                        # or when you press Ctrl-C a "Connection reset by peer" exception will be thrown

                        broadcast(c, "Client (%s, %s) quits" % c.sock.getpeername())
                        print "Client (%s, %s) quits" % c.sock.getpeername()
                        c.sock.close()
                        CONNECTIONS.remove(c)

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

    CONNECTIONS = []
    RECV_BUFFER=4096

    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 50116))
    server_socket.listen(10)
    server_socket.setblocking(0)

    threadlock = thread.allocate_lock()

    print "Chatterbox started"
    
    thread.start_new_thread(accept_connection, ())
    thread.start_new_thread(process_connection, ())

    try:
        while 1:
            pass
    except:
        server_socket.close()
