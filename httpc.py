
from urllib.parse import urlparse, parse_qs, urlencode
import argparse
import socket
import sys


class HTTPC:
    def __init__(self, host, port, path, data, file, overwrite, request):
        self.host = host
        self.port = port
        self.path = path
        self.data = data
        self.file = file
        self.overwrite = overwrite
        self.request = request

    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

    def get(self):
        if self.data or self.file:
            print("Do not pass data with GET request")
            sys.exit()

        self.connect()
        self.conn.send(self.request.encode())

        response = b""
        while True:
            data = self.conn.recv(1024)
            # print(data)
            if not data:
                break
            response += data
        try:
            response = response.decode("utf-8")
            # print(response)
        except UnicodeDecodeError:
            response = response.decode("iso-8859-1")

        self.conn.close()

        return response


    def post(self, overwrite):
        self.connect()

        if overwrite:
            self.request += f"Overwrite: {self.overwrite}\r\n"

        if self.file and self.data:
            print("Enter inline data or file. Not both!!")
            sys.exit()

        elif self.file:

            file = open(self.file, 'r')
            body = file.read()        

        elif self.data:
            body = self.data
           
        self.request += "Content-Type: application/json\r\n"
        self.request += f"Content-Length: {len(body)}\r\n\r\n"
        self.request += body
        print(self.request)
        self.conn.sendall(self.request.encode())

        response = b""
        while True:
            part = self.conn.recv(1024)
            if not part:
                break
            response += part
        response = response.decode("utf-8")

        self.conn.close()
        return response


def main():

    general = '''
    httpc is a curl-like application but supports HTTP protocol only.
    Usage:
    httpc command [arguments]
    The commands are:
    get executes a HTTP GET request and prints the response.
    post executes a HTTP POST request and prints the response.
    help prints this screen.
    Use "httpc help [command]" for more information about a command.

    '''
            
    get_usage = '''
    usage: httpc get [-v] [-h key:value] URL
    Get executes a HTTP GET request for a given URL.
    -v Prints the detail of the response such as protocol, status, 
    and headers.
    -h key:value Associates headers to HTTP Request with the format 
    'key:value'.

    '''
            
    post_usage = '''
    usage: httpc post [-v] [-h key:value] [-d inline-data] [-f file] URL
    Post executes a HTTP POST request for a given URL with inline data or from 
    file.
    -v Prints the detail of the response such as protocol, status, 
    and headers.
    -h key:value Associates headers to HTTP Request with the format 
    'key:value'.
    -d string Associates an inline data to the body HTTP POST request.
    -f file Associates the content of a file to the body HTTP POST 
    request.
    Either [-d] or [-f] can be used but not both.

   '''

    
    parser = argparse.ArgumentParser(prog="httpc", description="HTTP client application")
    parser.add_argument("method", choices=["get", "post", "help"], help="HTTP method (get or post)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    parser.add_argument("-H", "--header", action="append", help="Add a custom header (key:value)")
    parser.add_argument("-d", "--data", help="Inline data to include in the request body")
    parser.add_argument("-f", "--file", help="File to include in the request body")
    parser.add_argument("-o", "--write", help="write server response to a file")
    parser.add_argument("-r", "--overwrite", choices=["true", "false"], help="overwrite existing or not")
    parser.add_argument("url", help="URL to send the HTTP request to")

    args = parser.parse_args()
    if args.method.lower() == "help" and args.method.lower() not in ['post', 'get']:
        if args.url == "get":
            print(get_usage)
        elif args.url == "post":
            print(post_usage)
        else:
            print(general)
        sys.exit()
    if not args.url.startswith("http://") and not args.url.startswith("https://"):
        args.url = "http://" + args.url

    parsed_url = urlparse(args.url)
    query = parse_qs(parsed_url.query, keep_blank_values=True)
    query_string = urlencode(query, doseq=True)
    hostname = parsed_url.hostname
    path = parsed_url.path
    if query_string:
        path += "?" + query_string
    port = parsed_url.port or 80 

    headers = {}

    if args.header:
        for header in args.header:
            k, v = header.split(":")
            headers[k] = v

    request = f"{args.method.upper()} {path} HTTP/1.0\r\n"
    request += f"Host: {hostname}\r\n"
    for k, v in headers.items():
        request += f"{k}: {v}\r\n"

    httpc = HTTPC(hostname, port, path, args.data, args.file, args.overwrite, request)

    if args.method.lower() == "get" and args.method.lower() not in ['post', 'help']:
        try:
            response = httpc.get()
        except AttributeError:
            sys.exit()
            
    elif args.method == "post" and args.method.lower() not in ['get', 'help']:
        response = httpc.post(args.overwrite)

    else:
        print("Enter one of the following: 'help', 'get' or 'post'")

    # if not args.verbose:
    #     response = response.strip().split("\r\n\r\n", 1)[1]

    if args.write:
        file = open(args.write, 'w')
        file.write(response)
        file.close()
        print("Response successfully written to file")
    else:
        print(response)



if __name__ == '__main__':
    main()
    sys.exit()
