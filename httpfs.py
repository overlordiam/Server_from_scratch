import os
import argparse
import socket
import json
import re
import xml.etree.ElementTree as ET
import threading
import time


class Httpfs():

    def __init__(self, port, directory, verbose):
        self.port = port
        self.directory = directory
        self.verbose = verbose
        self.files = os.listdir(directory)
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
        if path == '/':
            if self.verbose:
                print('Responding with list of files')
                if return_type == 'plain':
                    for f in self.files:
                        response += f"{f}\n"

                elif return_type == 'json':
                    data = {"files": self.files}
                    response = json.dumps(data)

                elif return_type == 'xml':
                    root = ET.Element("files")
                    for f in self.files:
                        file_el = ET.SubElement(root, "file")
                        file_el.text = f
                    response = ET.tostring(root).decode()

                elif return_type == 'html':
                    response = "<html><body><ul>"
                    for f in self.files:
                        response += f"<li>{f}</li>"
                    response += "</ul></body></html>"

                else:
                    for f in self.files:
                        response += f + '\n'
                        
        elif re.search(r'\/\w+.\w+', path):
            path = path.strip('/')
            if self.verbose:
                print(f'Responding with contents of {path}')
            if path in self.files:
                theFile = open(self.directory + '/' + path, 'r')
                response = theFile.read() + '\n'
                theFile.close()
        else:
            if self.verbose:
                print(
                    f'Responding with HTTP 404 - file(s) not found {path}')
            response = 'HTTP 404 - file(s) not found\n'
        return response
    

    def post(self, data, path, overwrite='true'):
        path = path.strip('/')
        response = ''
        if path in self.files:
            if overwrite.lower() == "true":
                if self.verbose:
                    print("Responding with data overwritten to file', path")
                theFile = open(self.directory + '/' + path, 'w+')
                theFile.write(data)
                theFile.close()
                response = 'Data overwritten to file '+path
            else:
                res = f"File: {path} already exists. Not overwriting!!"
                response += res
                print(res)

        elif path not in self.files:
            if self.verbose:
                print("Responding with data written to new file '+ path")
            theFile = open(self.directory + '/' + path, 'w+')
            theFile.write(data)
            theFile.close()
            response = 'Data written to new file ' + path
        else:
            if self.verbose:
                print("Responding with HTTP 403 - action refused")
            response = "HTTP 403 - action refused \n"
        return response

def handle_new_client(conn, httpfs):
    print("1st line of handle_client")
    request = conn.recv(1024).decode("utf-8")
    request = request.split('\r\n')
    print(request)
    method_path_var = request[0].split()
    method = method_path_var[0]
    path = method_path_var[1]
    overwrite = ''
    return_type = ''

    index = request.index('')
    for header in request[2:index]:
        if 'Overwrite' in header:
            overwrite = header.split(":")[1]
        
        if 'Accept' in header:
            return_type = header.split(":")[1].split("/")[1]
            
    data = ''
    for l in request[index+1:]:
        data += l + '\n'

    response = ''
    if method == 'GET':
        response = httpfs.get(path, return_type)
    elif method == 'POST':
        response = httpfs.post(data, path, overwrite)

    print(response)

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
    # print("Before object initialization")

    httpfs = Httpfs(args.port, directory, args.verbose)

    if httpfs.verbose:
        print(f'Httpfs server is listening at port : {httpfs.port}')

    TIMEOUT = 10000
    start_time = time.time()
    while True:
        conn, _ = httpfs.server.accept()
        start_time = time.time()
        print("here")
        t = threading.Thread(target=handle_new_client, args=(conn, httpfs))
        t.start()
        
        if time.time() - start_time > TIMEOUT:
            break

    httpfs.disconnect()

if __name__ == "__main__":
    main()   