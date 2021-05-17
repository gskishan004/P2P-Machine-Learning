import socket
import threading
from note import Note
from course import Course


class Server:
    lecture_outline = ""
    connections = []
    peers = []

    def __init__(self, name, course, note):

        self.username = name
        self.course = course
        self.note = note
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', course.course_port))
        sock.listen(1)

        print(self.username + " is now the Facilitator in this classroom...")

        while True:
            c, a = sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0])
            print(str(a[0]) + ':' + str(a[1]), "connected")
            self.sendPeers()

    def handler(self, c, a):
        while True:
            data = c.recv(1024)

            if not data:
                print(str(a[0]) + ':' + str(a[1]), "disconnected")
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break

            elif data[0:4] == b'::ml':
                data_to_send = "[ML IMG -> TXT] \n -*10 \n".encode('UTF-8') + data[4:]
                self.broadcast(data_to_send)

            elif data[0:2] == b'::':
                data_to_send = "[chat] ".encode('UTF-8') + data[2:]
                self.broadcast(data_to_send)



            else:
                print(a, ":", data.decode('UTF-8'))
                self.note.body = self.note.body + data.decode('UTF-8') + "\n"
                self.broadcast(data)

    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + peer + ","

        for connection in self.connections:
            connection.send(b'\x11' + bytes(p, 'utf-8'))

    def broadcast(self, data_to_broadcast):
        for connection in self.connections:
            connection.send(bytes(data_to_broadcast))


