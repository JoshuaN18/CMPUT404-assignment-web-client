#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust and Joshua Nam
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse
from urllib.parse import urlparse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None


    def get_code(self, headers):
        return int(headers.split()[1])


    def get_headers(self, data):
        return data.split('\r\n\r\n')[0]


    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        

    def close(self):
        self.socket.close()


    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')


    def GET_header(self, host_name, path):
        # Create the GET header
        request = "GET " + path + " HTTP/1.1\r\n"
        host = "Host: " + host_name + '\r\n'
        connection = "Connection: close\r\n\r\n"
        return request + host + connection


    def GET(self, url, args=None):
        # Parse the url and get the host and path
        url_parse = urlparse(url)
        host_name = url_parse.hostname
        path = url_parse.path if url_parse.path != '' else '/' 
        
        # Get the header
        header = self.GET_header(host_name, path)

        # Get the port and connect to server
        port = url_parse.port if url_parse.port != None else 80
        self.connect(host_name, port)
        self.sendall(header)
        data = self.recvall(self.socket)

        # headers, code and body
        headers = self.get_headers(data)
        code = self.get_code(headers)
        body = self.get_body(data)

        self.close()
        return HTTPResponse(code, body)


    def POST_header(self, host_name, path, length, body):
        # Create the POST header
        request = "POST " + path + " HTTP/1.1\r\n"
        host = "Host: " + host_name + '\r\n'
        content_type = "Content-Type: application/x-www-form-urlencoded\r\n"
        content_length = "Content-Length: " + str(length) + "\r\n"
        connection = "Connection: close\r\n\r\n"
        return request + host + content_type + content_length + connection + body


    def POST(self, url, args=None):  
        # Parse the url and get the host and path
        url_parse = urlparse(url)
        host_name = url_parse.hostname
        path = url_parse.path if url_parse.path != '' else '/' 

        # Get the body
        length = 0
        body = "" 
        if args:
            body = urllib.parse.urlencode(args)
            length = len(body)

        # Get the header
        header = self.POST_header(host_name, path, length, body)

        # Get the port and connect to server
        port = url_parse.port if url_parse.port != None else 80
        self.connect(host_name, port)
        self.sendall(header)
        data = self.recvall(self.socket)

        # headers, code and body
        headers = self.get_headers(data)
        code = self.get_code(headers)
        body = self.get_body(data)

        self.close()     
        return HTTPResponse(code, body)


    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    

if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))