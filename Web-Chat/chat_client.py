import socket
import thread
import sys
import Tkinter
from Tkinter import *
from ClientGUI import ClientGUI
import Queue

HOST = "127.0.0.1"
PORT = 50116
#HOST = raw_input("Please enter the Host IP\n")
#PORT = int(raw_input("Please enter the Port number\n"))
RECV_BUFFER=4096
ready = False

#GUI thread. The window is created and configured here whereas the Widgets are created in the object gui
def generate_GUI():
    global gui, ready
    root = Tk()
    root.wm_title("Chatterbox")
    root.wm_iconbitmap('Chatterbox.ico')
    gui = ClientGUI(root)
    ready = True
    root.geometry('600x600')
    gui.write("Please enter a user name")
    gui.write("Enter a message with the Enter key. To quit, type \"/logout\"")
    while 1:
        root.mainloop()

#Function that receives data from other clients connected to server
def recv_data():
    global gui
    while 1:
        try:
            recv_data = client_socket.recv(RECV_BUFFER)            
        except:
            #Handle the case when server process terminates
            print "Server closed connection, thread exiting."
            thread.interrupt_main()
            break
        if recv_data:
            gui.write(recv_data)
        else:
            # Recv with no data, server closed connection
            print "Server closed connection, thread exiting."
            thread.interrupt_main()
            break

#Function that sends data from other clients connected to the server
def send_data():
    global gui

    while 1:
        try:
            if gui.text_input:
                text_input = gui.text_input
                #print "bingo" +text_input
                gui.text_input = ""
                data_list = text_input.split(" ", 2)
                if len(data_list) >= 3:
                    if data_list[1] == "username":
                      username = data_list[2]
                      client_socket.send(text_input)
                    else:
                        client_socket.send(text_input)
                else:
                    client_socket.send(text_input)
        except:
            pass
        
if __name__ == "__main__":

    print "Connecting to server at %s:%s" % (HOST, PORT)
    print "Enter a message with the Enter key. To quit, type \"/logout\""

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print "Connected to server at %s:%s" % (HOST, PORT)

    thread.start_new_thread(generate_GUI,())
    while ready == False:
        pass
    thread.start_new_thread(send_data,())
    thread.start_new_thread(recv_data,())


    try:
        while 1:
            continue
    except:
        print "Client program quits...."
        client_socket.close()
        
    
    


