from Tkinter import *
import Queue
import os


class ClientGUI(Text):
    """GUI for client chat. Implements a queue to allow for threadsafe writes to the text window"""


    def __init__(self, root, **options):

        Text.__init__(self, root, **options)
        self.root = root
        
        #Creates the receiver window
        self.server_text = Text(root, height = 30, width = 100)
        self.server_text.pack(side = TOP, fill = "both")
        self.server_text.configure(state = 'disabled')

        #Creates the sender window
        self.user_text = Text(root, height = 10, width = 200)

        #Creates the send button, sets the button click to execute retrieve_input_click() (which couldn't be overloaded for some reason)
        self.b = Button(root, width = 10, text="Send", command = self.retrieve_input_click)
        self.b.pack(side = RIGHT, fill = "both")

        #Configures the sender window
        self.user_text.pack(side = BOTTOM, fill = "both", expand = True)
        self.user_text.bind('<Return>', self.retrieve_input) #binds the function retrieve_input to Enter key in the sender window
        self.text_input = ""

        #Creates the queue object
        self.queue = Queue.Queue()
        self.update()
    
    #Updates the queue and inserts the longest queued string
    def update(self):
        try:
            while 1:
                line = self.queue.get_nowait()
                if line is None:
                    self.delete(1.0, END)
                else:
                    self.server_text.configure(state='normal')
                    self.server_text.insert(END, str(line))
                    self.server_text.configure(state='disabled')
                self.see(END)
                self.root.update_idletasks()
        except Queue.Empty:
            pass
        self.root.after(100, self.update)

    def clear(self):
        self.queue.put(None)

    #The method called outside of the thread. If a queue wasn't implemented we would get an infinite loop error
    def write(self, message):
        self.queue.put(message + "\n")

    #Grabs the line from the sender window, then clears the window out. return 'break' prevents the cursor from going to the next line
    def retrieve_input(self, event):
        self.text_input = self.user_text.get("1.0",'end-1c')
        self.user_text.delete("1.0", 'end')
        return 'break'

    def retrieve_input_click(self):
        self.text_input = self.user_text.get("1.0",'end-1c')
        self.user_text.delete("1.0", 'end')
