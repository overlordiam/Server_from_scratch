import socket
import threading
import random

HOST = 'localhost' 
PORT = 8080


def client_write():
  
    sock = socket.socket()
    sock.connect((HOST, PORT))
    data = random.random()
    data = str(data)

    request = f"POST /foo HTTP/1.0\r\n"
    request += f"Host: {HOST}\r\n"
    request += "Content-Type: application/json\r\n"
    request += f"Content-Length: {len(data)}\r\n\r\n"
    request += data
    sock.send(request.encode())

    response = sock.recv(1024)
    print(response.decode('utf-8'))

    sock.close()


def client_read():
  
    sock = socket.socket()
    sock.connect((HOST, PORT))
    data = random.random()
    data = str(data)

    request = f"GET /foo HTTP/1.0\r\n"
    request += f"Host: {HOST}\r\n"
    sock.send(request.encode())

    response = sock.recv(1024)
    print(response.decode('utf-8'))

    sock.close()



def multiple_reads_and_writes(count):

  threads = []    
  for _ in range(count):
    t = threading.Thread(target=client_write)
    threads.append(t)
    t1 = threading.Thread(target=client_read)
    threads.append(t1)
    
  for t in threads:
    t.start()

def multiple_writes(count):
  threads = []    
  for _ in range(count):
    t = threading.Thread(target=client_write)
    threads.append(t)
      
  for t in threads:
    t.start()

def multiple_reads(count):
  threads = []    
  for _ in range(count):
    t = threading.Thread(target=client_read)
    threads.append(t)
      
  for t in threads:
    t.start()

if __name__ == '__main__':
    multiple_reads_and_writes(3)
