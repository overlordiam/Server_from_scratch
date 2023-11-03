import socket
import threading
import random

HOST = 'localhost' 
PORT = 8080


def client_thread():
  
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

def run_clients():

  threads = []

  for _ in range(5):
    
    t = threading.Thread(target=client_thread)
    # t.start()
    threads.append(t)
    
  for t in threads:
    t.start()

  # for t in threads:
  #   t.join()
        
if __name__ == '__main__':

  run_clients()
