import os
import argparse
import socket
import json
import re
import xml.etree.ElementTree as ET
import threading
import time
import random


class Httpfs():

    def __init__(self, port, directory, verbose):
        self.port = port
        self.directory = directory
        self.verbose = verbose
        self.server = self.connect()


    def connect(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        server.listen(5)
        return server
    
    def disconnect(self):
        self.server.close()

    def get(self, path, return_type):
        response = ''
        files = os.listdir(self.directory)
        if path == '/':
            if self.verbose:
                print('Responding with list of files')
                if return_type == 'plain':
                    for f in files:
                        response += f"{f}\n"

                elif return_type == 'json':
                    data = {"files": files}
                    response = json.dumps(data)

                elif return_type == 'xml':
                    root = ET.Element("files")
                    for f in files:
                        file_el = ET.SubElement(root, "file")
                        file_el.text = f
                    response = ET.tostring(root).decode()

                elif return_type == 'html':
                    response = "<html><body><ul>"
                    for f in files:
                        response += f"<li>{f}</li>"
                    response += "</ul></body></html>"

                else:
                    for f in files:
                        response += f + '\n'
                        
        elif re.search(r'\/\w+.\w+', path):
            path = path.strip('/')
            if self.verbose:
                print(f'Responding with contents of {path}')
            if path in files:
                theFile = open(self.directory + '/' + path, 'r')
                response = theFile.read() + '\n'
                theFile.close()
        else:
            if self.verbose:
                print(
                    f'Responding with HTTP 404 - file(s) not found {path}')
            response = 'HTTP 404 - file(s) not found\n'
        return response
    

    def post(self, data, path, overwrite):
        path = path.strip('/')
        response = ''
        lock = threading.RLock()

        lock.acquire()
        files = os.listdir(self.directory)
        lock.release()
        if path in files:
            if overwrite:
                if self.verbose:
                    print("Responding with data overwritten to file', path")
                
                lock.acquire()
                time.sleep(3)
                theFile = open(self.directory + '/' + path, 'w+')
                theFile.write(data)
                print(data)
                theFile.close()
                lock.release()

                response = 'Data overwritten to file '+ path

            else:
                
                lock.acquire()
                time.sleep(3)
                theFile = open(self.directory + '/' + path, 'r')
                file_data = theFile.read()
                file_data = file_data + data
                print("else: ", file_data)
                fileWrite = open(self.directory + '/' + path, 'w+')
                fileWrite.write(file_data)
                theFile.close()
                lock.release()

        elif path not in files:
            if self.verbose:
                print("Responding with data written to new file '+ path")
           
            lock.acquire()
            theFile = open(self.directory + '/' + path, 'w+')
            theFile.write(data)
            theFile.close()
            lock.release()

            response = 'Data written to new file ' + path
        else:
            if self.verbose:
                print("Responding with HTTP 403 - action refused")
            response = "HTTP 403 - action refused \n"
        return response

def handle_new_client(conn, httpfs):
    request = conn.recv(1024).decode("utf-8")
    request = request.split('\r\n')
    # print(request)
    method_path_var = request[0].split()
    method = method_path_var[0]
    path = method_path_var[1]
    return_type = ''
    overwrite = False

    index = request.index('')
    for header in request[2:index]:
        if 'Overwrite' in header:
            overwrite = True
            break
    
    for header in request[2:index]:    
        if 'Accept' in header:
            return_type = header.split(":")[1].split("/")[1]
            break
            
    data = ''
    for l in request[index+1:]:
        data += l + '\n'

    response = ''

    # time.sleep(3)

    if method == 'GET':
        response = httpfs.get(path, return_type)
    elif method == 'POST':
        response = httpfs.post(data, path, overwrite)
    

    # print(response)

    conn.sendall(response.encode('utf-8'))
    conn.close()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='verbosity', action='store_true')
    parser.add_argument(
        '-p', '--port', help='Specify port - Default is 8080', type=int, default=8080)
    parser.add_argument('-d', '--directory',
                        help='Specify directory - Default is current', type=str, default='temp')

    args = parser.parse_args()

    directory = args.directory
    if directory is None:
        directory = os.path.dirname(os.path.realpath(__file__))

    httpfs = Httpfs(args.port, directory, args.verbose)

    if httpfs.verbose:
        print(f'Httpfs server is listening at port : {httpfs.port}')

    while True:
        conn, _ = httpfs.server.accept()
        t = threading.Thread(target=handle_new_client, args=(conn, httpfs))
        t.start()


    # httpfs.disconnect()

if __name__ == "__main__":
    main()   