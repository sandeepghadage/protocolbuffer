#!/usr/bin/python
#!/usr/bin/python           # This is server.py file
# pylint: disable = no-member
# pylint: disable = missing-docstring
# pylint: disable = global-statement
# pylint: disable = too-many-statements
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import base64
import redis
import ex_pb2
import logging
import cgi

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def end_headers (self):
       self.send_header('Access-Control-Allow-Origin', '*')
       BaseHTTPRequestHandler.end_headers(self)

    def do_GET(self):

        pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
        server = redis.Redis(connection_pool=pool)

        lst = self.path.split(",")


        self.send_response(200)  # OK
        self.send_header('Content-type', 'text/html')
        #self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write('{name : ashish}')


        return


    def do_POST(self):

        pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
        server = redis.Redis(connection_pool=pool)


        form = cgi.FieldStorage(
        fp=self.rfile,
        headers=self.headers,

        environ={'REQUEST_METHOD':'POST',
                'CONTENT_TYPE':self.headers['Content-Type'],
                 })

        print self.rfile
        print self.headers

        logging.warning("======= POST VALUES =======")
        
        for item in form.list:
            print item



        self.send_response(200)  # OK
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('HelloWorld')

       
        return


def main():

    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(("localhost", PORT_NUMBER), myHandler)
        print "Started httpserver on port ", PORT_NUMBER

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C received,  shutting down the web server"
        server.socket.close()

if __name__ == "__main__":
    main()
