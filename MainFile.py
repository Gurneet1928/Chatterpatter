import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import socket
import threading
from threading import Thread

#-------------------------------------SERVER/PORT/GLOBAL VARIABLES DETAILS-----------------------------------------

PORT = 0                            #PORT = 0  for selecting any available Port
AVAILABLE_PORT=0
SERVER = socket.gethostbyname(socket.gethostname())         #Getting current IP of the host
conn_addr = []
FORMAT = "utf-8"                    #Default Format
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
i_cs=0
i_jr=0
client_data=[]                      #List to store the data of all the clients connected
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           #Socket for Create Room's Self Client
client_socket_joinroom = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #Socket for Join Room's Client
default_font=('HP Simplified Jpan','11')

#-------------------------------------ALL REQUIRED FUNCTIONS-----------------------------------------

def listen():                   #Main Function to Start the Server Room
    global conn_addr
    global client_data
    global AVAILABLE_PORT
    global SERVER
    global FOMART
    global chatbox
    global i_cs
    s.bind((SERVER,0))
    AVAILABLE_PORT = s.getsockname()[1]
    s.listen()
    rctext = f" The Room code is : {AVAILABLE_PORT}"
    tk.Label(create_room, text=rctext,font=('8')).grid(row=1, column=2)
    while True:
        conn, addr = s.accept()
        print(conn)
        conn_addr.append(conn)
        conn_addr.append(addr)
        client_data.append(conn)
        msg = conn.recv(1024).decode(FORMAT)
        chatbox.insert(i_cs,msg)
        i_cs=i_cs+1
        threading.Thread(target=handle_client,args=(conn,addr)).start()
        threading.Thread(target=recmsg,args=(conn,)).start()


def handle_client(conn,addr):           #Function to handle new connections and print them on Console. ONLY FOR USE BY DEVELOPER TO TRACK CONNECTIONS
    global i_cs
    global chatbox
    print(f'[NEW CONNECTION {conn} connected.]')

t_listen = lambda: [threading.Thread(target=listen).start() ,threading.Thread(target=selfclient).start()]

def serverstart():                      #Creates only Chatbox and adds the pre-defined text in it
    global i_cs
    global conn_addr
    global chatbox
    chatbox.grid(row=3, columnspan=3)
    chatbox.insert(i_cs, "WELCOME TO THE CHAT ROOM")
    i_cs = i_cs+1
    chatbox.insert(i_cs, "WHEN SOMEONE JOINS , THERE NAMES WILL BE SHOWN HERE")
    i_cs = i_cs+1
    ipaddmessage = f"ROOM IP :: {conn_addr[1][0]} AND CODE :: {conn_addr[1][1]}"
    chatbox.insert(i_cs,ipaddmessage)
    i_cs = i_cs+1

def selfclient():                       #Creates a In-Built Client for the person who creates a Server , making it easy to chat from the same page
    global AVAILABLE_SERVER
    global AVAILABLE_PORT
    global client_socket
    global msg_create_room
    global startroom_button
    client_socket.connect((SERVER,AVAILABLE_PORT))
    client_socket.send(bytes("YOU HAVE JOINED THE CHAT","utf-8"))
    tk.Label(create_room,text=" Enter Your Name Here\n(Anonymous is left Blank) ",font=default_font).grid(row=1,column=3)
    tk.Entry(create_room, textvariable=username_self, width=20, border=4,font=default_font).grid(row=2, column=3)
    tk.Entry(create_room, textvariable=msg_create_room,width=60,border=4,font=default_font).grid(row=4, columnspan=3)
    tk.Button(create_room,text="Send Message",border=4,width=20,font=default_font,command=lambda:threading.Thread(target=sendmsg).start()).grid(row=4,column=3)
    tk.Button(create_room,text="Close the room",command=closeroom,border=4,background="black",foreground="white",font=default_font).grid(row=6,columnspan=3)

def closeroom():                        #Function to close that Chat Room Server
    global conn_addr
    global chatbox
    global i_cs
    chatbox.delete(0,i_cs-1)
    chatbox.insert(i_cs,"CHAT ROOM CLOSED ! THANK YOU")
    conn_addr[0].close()


def sendmsg():                          #Function to send the chats to server , will be used by Self Client
    global msg_create_room
    global client_socket
    global username_self
    global FORMAT
    msg = msg_create_room.get()
    uname = username_self.get()
    if uname!='':
        msg = uname + " >> " + msg
    else:
        msg = "Anonymous >> " + msg

    client_socket.send(bytes(msg,FORMAT))


def recmsg(conn):                          #Function for Server , to receieve and send messages to various client and adds them to chatbox as well
    global chatbox
    global i_cs
    global client_data
    global FORMAT
    while True:
        msg = conn.recv(1024).decode(FORMAT)
        chatbox.insert(i_cs, msg)
        i_cs = i_cs + 1
        for x in client_data:
            if x!=conn:
                x.send(bytes(msg, FORMAT))

def joinroomwithcode():                     #Function for Join Room , connects the Client to Server
    global i_jr
    global chatbox2
    global client_socket_joinroom
    global msg_join_room
    global FORMAT
    global username_join
    roomcode = room_code.get()
    if roomcode.isdigit() and int(roomcode)>1024 and int(roomcode)<65535:
        ADDR_joinroom = (socket.gethostbyname(socket.gethostname()),int(roomcode))
        try:
            client_socket_joinroom.connect(ADDR_joinroom)
            chatbox2.grid(row=3, column=1, columnspan=3, rowspan=3)
            chatbox2.insert(i_jr,"WELCOME TO CHATROOM ")
            i_jr=i_jr+1
            chatbox2.insert(i_jr,f"YOU HAVE JOINED ROOM :: {roomcode}")
            i_jr = i_jr + 1
            client_socket_joinroom.send(bytes("SOMEONE POPPED INTO THE CHAT",FORMAT))
            tk.Label(join_room, text=" Enter Your Name Here\n(Anonymous is left Blank) ",font=default_font).grid(row=1, column=4)
            tk.Entry(join_room, textvariable=username_join, width=20, border=4,font=default_font).grid(row=2, column=4)
            tk.Entry(join_room, textvariable=msg_join_room,width=60,border=4,font=default_font).grid(row=7, column=1,columnspan=3)
            tk.Button(join_room, text="Send Message",font=default_font, command=lambda: [threading.Thread(target=sendmsg_joinroom,args=(client_socket_joinroom,)).start()]).grid(row=7, column=4)
            threading.Thread(target=recmsg_joinroom,args=(client_socket_joinroom,)).start()
        except:
            messagebox.showerror("ERROR", "INVALID ROOM CODE !! PLEASE TRY AGAIN")
            exit(0)
    else:
        messagebox.showerror("ERROR","INVALID ROOM CODE !! PLEASE TRY AGAIN")

def recmsg_joinroom(conn):                  #Function for Client, Receives message from Server and adds them to chatbox
    global i_jr
    global chatbox2
    global FORMAT
    while True:
        msg = conn.recv(1024).decode(FORMAT)
        chatbox2.insert(i_jr,msg)
        i_jr = i_jr+1

def sendmsg_joinroom(conn):                 #Fucntion for Client, Sends message to Server and adds them to Chatbox as well
    global i_jr
    global chatbox2
    global msg_join_room
    global FORMAT
    global username_join
    msg = msg_join_room.get()
    uname = username_join.get()
    if uname!='':
        msg = uname + " >> " + msg
    else:
        msg = "Anonymous >> "+msg
    conn.send(bytes(msg,FORMAT))
    chatbox2.insert(i_jr,msg)
    i_jr=i_jr+1


#-------------------------------------GUI STARTS HERE-----------------------------------------

#------------Only Declaration of Frame and Tabs----------------
root = tk.Tk()
root.title("Chatterpatter")
root.geometry('780x760')

style = ttk.Style(root)
style.configure('lefttab.TNotebook', tabposition='n')
style.configure('TNotebook.Tab', padding=(10, 0, 20, 0))
notebook = ttk.Notebook(root, style='lefttab.TNotebook')
notebook.pack(fill='both')

create_room = ttk.Frame(notebook,width=600,height=440)
join_room = ttk.Frame(notebook,width=600,height=440)
instructions = ttk.Frame(notebook,width=600,height=440)

create_room.pack(fill='both', expand=True)
join_room.pack(fill='both', expand=True)
instructions.pack(fill='both',expand=True)

create_room_img = PhotoImage(file=r"images\create_room.png")
join_room_img = PhotoImage(file=r"images\join_room.png")
instructions_img = PhotoImage(file=r"images\instructions.png")

notebook.add(create_room,text="CREATE A ROOM",compound="top",image=create_room_img)
notebook.add(join_room,text=" JOIN A ROOM ",compound="top",image=join_room_img)
notebook.add(instructions,text=" INSTRUCTIONS ",compound="top",image=instructions_img)

#-------------------------------------CREATE A ROOM TAB-----------------------------------------
tk.Label(create_room,text="\t\t").grid(row=0,column=0)
chatbox = tk.Listbox(create_room,activestyle=tk.DOTBOX,border=4, width=60,height=25,font=default_font)
msg_create_room = tk.StringVar()
username_self = tk.StringVar()
tk.Button(create_room,text=" CLICK HERE TO GENERATE ROOM CODE ",command=t_listen,background="brown",foreground="white",border=4,font=default_font).grid(row=1,column=1)
tk.Button(create_room,text=" CLICK HERE TO START ROOM ",background="red",foreground="white",border=4,font=default_font,command=lambda:[threading.Thread(target=serverstart()).start()]).grid(row=2, column=1)


#-------------------------------------JOIN A ROOM TAB-----------------------------------------

chatbox2 = tk.Listbox(join_room,activestyle=tk.DOTBOX,border=4, width=60,height=25,font=default_font)
room_code = tk.StringVar()
tk.Label(join_room,text="\t").grid(row=0,column=0)
tk.Label(join_room,text="Enter the Room Code here as it is :: ",font=('HP Simplified Jpan', '12')).grid(row=1,column=1)
tk.Entry(join_room,textvariable=room_code,border=4,width=15,font=('HP Simplified Jpan', '12')).grid(row=1,column=2)
tk.Button(join_room,text="Join Room",border=3,width=15,background='black',foreground='white',font=default_font,command=lambda:[threading.Thread(target=joinroomwithcode).start()]).grid(row=1,column=3)
msg_join_room =tk.StringVar()
username_join = tk.StringVar()

#-------------------------------------INSTRUCTIONS-----------------------------------------

tk.Label(instructions,text=">> INSTRUCTIONS TO USE THE PROGRAM <<",font=('HP Simplified Jpan', '12','underline')).grid(row=1,column=0)
tk.Label(instructions,text=">> TO CREATE A SERVER AND USE IT",font=('HP Simplified Jpan', '12'),justify="left").grid(row=2,column=0)
tk.Message(instructions,width=750,font=('HP Simplified Jpan', '12'),text=" 1> Click on \"Generate Room Code\" Button First .It will Generate and show a room Code\n"
                             " 2> Share the room code with others so that they can also join the same room\n"
                             " 3> You can also enter your Username on the right side , which you want others to see \n"
                             " 4> After doing all the stuffs, make sure to click on \"Close the Room\" button , so as to make sure that room and server is closed and port is made free\n").grid(row=3,column=0)
tk.Label(instructions,text=">> TO CREATE JOIN A SERVER",font=('HP Simplified Jpan', '12'),justify="left").grid(row=4,column=0)
tk.Message(instructions,width=750,font=('HP Simplified Jpan', '12'),text=" 1> Enter the Room code in the box and Click on \"Join Room\"\n"
                             " Note:: Make sure to enter the room code correctly and only Numberics are allowed , otherwise error will be thrown\n"
                             " 2> You can also enter your Username on the right side , which you want others to see \n"
                             " 3> Feel Free to leave anytime from this side.\n").grid(row=5,column=0)


root.mainloop()

#----------------------------------END OF CODE---------------------------------------