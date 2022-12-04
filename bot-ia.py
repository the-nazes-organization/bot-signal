#Write a class that is a bot to signal messages to a user
#The bot should be able to send a message to a user
#The bot should be able to read a message from a user
#The bos is connected to a websocket
#the websocket read 1024 octect at a time
#the bot continuously reading messages

import socket
import threading
import time
import random
import string

class Bot():

        def __init__(self, name):
            self.name = name
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.attached = False
            self.buffer = ""

        def attach(self,port):
            self.port = port
            self.s.connect(('localhost',self.port))
            self.connected= True
            time.sleep(1)

        def sendMessage(self,msg):
            self.s.send(msg.encode('utf-8'))

        def getMessage(self):
            self.subread()
            if(self.buffer):
                i = self.buffer.find("\n")
                remainingMessage = ""
                if(i>-1):
                    tempMessage = self.buffer[:i]
                    remainingMessage = self.buffer[i+1:]
                    print(remainingMessage)
                return remainingMessage
            return ""

        def subread(self):
            size=2048
            self.buffer += self.s.recv(sizeof(self.buffer)).decode('utf-8')

        def desattach(self):
            self.s.close()
            self.connected = False

class ThreadBotClient(threading.Thread):
        def __init__(self,n):
            threading.Thread.__init__(self)
            self.n=n
            self.b=Bot(self.n)
            self.t0=time.time()
            self.changeAlso= True

        def run(self):
            print('the Bot thread init '+self.n)
            self.b.sendMessage('register '+ self.n+' \n')
            while True:
                time.sleep(random.uniform(2,5))
                msg= ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase) for _ in range(10))
                if self.changeAlso == True:
                    msg2 = ''.join(random.choice(string.ascii_uppercase+string.ascii_lowercase) for _ in range(10))
                    self.b.sendMessage('Boto '+msg2+' new text changed\n')
                    self.changeAlso= False

                self.b.sendMessage(self.n+' '+msg+' \n')
                print('SELF '+self.n+' '+msg)
                source=self.b.getMessage()
                while source :
                    print( 'other '+source)
                    source=self.b.getMessage()

            print('finish thread bot')

class ThreadUserConsole(threading.Thread):
        def __init__(self,name):
            threading.Thread.__init__(self)
            self.c = Bot(name)
            self.c.bind_and_listen()

        def run(self):
            while True:
                answer = input()
                if not answer:
                    continue
                elif answer == "quit" or answer== "exit":
                    self.c.exit()
                    return
                elif answer:
                    self.c.send_message(answer)


if __name__ == '__main__':
        random.seed()
        print('welcome to python chat\nenter your name :')
        name = input()
        thread_userConsole = ThreadUserConsole(name)
        thread_userConsole.start()