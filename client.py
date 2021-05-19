import socket
import multiprocessing
import sys
import time
from course import Course
from note import Note
from datetime import datetime
from img2txt import img2txt

class Client:
    def __init__(self, name, address, course, note):
        self.name = name
        self.note = note
        self.course = course
        self.ml_node_list = ["ml_node"]
        self.p2paddress = '127.0.0.1'
        self.port = None


        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.connect((address, course.course_port))
        except:
            return

        self.iThread = multiprocessing.Process(target = self.sendMsg, args=(sock, ))
        self.iThread.daemon = True
        self.iThread.start()
        

        print("You have joined " + self.course.course_name + "'s room. Welcome!")

        sock.send(b"User:" +bytes(name, 'utf-8'))

        while True:
            data = sock.recv(1024)
            if not data:
                #print('the server disappeared!')
                self.iThread.terminate()
                self.iThread.close()
                time.sleep(2)
                #print("thread dead --------------------------> ",self.iThread.is_alive())
                break
            
            # server side messages during initial connection
            # this 
            if data[0:1] == b'\x11' and self.p2paddress == '127.0.0.1':
                self.peersUpdated(data[1:])
                self.p2paddress = P2P.peers[-1]
                self.port = self.p2paddress.split(":")[-1]

            # server side messages during new peer connection
            elif data[0:1] == b'\x11':
                self.peersUpdated(data[1:])
            
            # server side messages during initial connection, part 2
            # this sets P2P.peer_with_name for each client
            elif data[0:10] == b'All_Users:':
                temp_Data = data[10:-1].decode('UTF-8')
                temp_set = set()
                for name in temp_Data.split(","):
                    temp_set.add(name)
                
                P2P.peer_with_name= temp_set

            
            elif data[0:4] == b'[ML]' and self.name in self.ml_node_list:
                print("Broadcasting ML data")
                file_name = data[4:].strip()
                img2txt_instance = img2txt()
                data_to_broadcast = '::ml ' + img2txt_instance.convert(file_name)
                sock.send(bytes(data_to_broadcast, 'utf-8'))

            else:
                self.note.body = self.note.body + data.decode('UTF-8') + "\n"
                print("[note] " + str(data, "utf-8"))


    def peersUpdated(self, peerData):
        P2P.peers = str(peerData, "utf-8").split(",")[:-1]

    

    def sendMsg(self, sock):
        sys.stdin = open(0)
        while True:
            try:
                user_input = input("")
            except:
                user_input = "NULL"

            if user_input == "savehistory()":
                self.save_history()
            elif user_input!="NULL":
                try:
                    sock.send(bytes(user_input, 'utf-8'))
                except:
                    print('Resend the messsage, cleaning up the nodes')
                    break

    def save_history(self):
        filename = self.course.course_name + "-note-" + str(datetime.now().date())
        with open(filename, 'w') as f:
            f.write(self.note.body)
        f.close()
        print("The history has been saved to your local directory.")


class P2P:
    peers = ['127.0.0.1']
    peer_with_name = set()
