import os
import argparse
import socket
import re


class Httpfs():

    def __init__(self, port, directory, verbose):
        self.port = port
        self.directory = directory
        self.verbose = verbose
        self.files = os.listdir(directory)
        # print("in constructor, before connect")
        self.server = self.connect()
        # print("in constructor, after connect")


    def connect(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', self.port))
        server.listen(5)
        return server


    def get(self, path):
        response = ''
        if path == '/':
            if self.verbose:
                print('Responding with list of files')
                for f in self.files:
                    response += f + '\n'
            elif re.search(r'\/\w+.\w+', path):
                path = path.strip('/')
                if self.verbose:
                    print(f'Responding with contents of {path}')
                if path in self.files:
                    theFile = open(self.directory + '/' + path, 'r')
                    #print(f'File: {theFile}')
                    response = theFile.read() + '\n'
                    theFile.close()
                else:
                    if self.verbose:
                        print(
                            f'Responding with HTTP 404 - file(s) not found {path}')
                    response = 'HTTP 404 - file(s) not found\n'
        return response
    

    def post(self, data, path):
        path = path.strip('/')
        response = ''
        if path in self.files:
            if self.verbose:
                print("Responding with data overwritten to file', path")
            theFile = open(self.directory + '/' + path, 'w+')
            theFile.write(data)
            theFile.close()
            response = 'Data overwritten to file '+path
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


def main(httpfs):

    if httpfs.verbose:
        print(f'Httpfs server is listening at port : {httpfs.port}')
    while True:
        conn, _ = httpfs.server.accept()
        request = conn.recv(1024).decode("utf-8")
        request = request.split('\r\n')
        method_path_var = request[0].split()
        method = method_path_var[0]
        path = method_path_var[1]

        # print(f'Method {method}')
        # print(f'Path: {path}')

        index = request.index('')
        data = ''
        for l in request[index+1:]:
            data += l + '\n'

        response = ''
        # reg_ex = re.search(r'\/\w+.\w+', path)
        if method == 'GET':
            response = httpfs.get(path)
        elif method == 'POST':
            response = httpfs.post(data, path)
        
        print(response)


        conn.sendall(response.encode('utf-8'))
        conn.close()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='verbosity', action='store_true')
    parser.add_argument(
        '-p', '--port', help='Specify port - Default is 8080', type=int, default=8080)
    parser.add_argument('-d', '--directory',
                        help='Specify directory - Default is current', type=str)
    args = parser.parse_args()

    directory = args.directory
    if directory is None:
        directory = os.path.dirname(os.path.realpath(__file__))
    # print("Before object initialization")

    httpfs = Httpfs(args.port, directory, args.verbose)

    main(httpfs)   