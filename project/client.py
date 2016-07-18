#!/usr/bin/python           # This is client.py file
# pylint: disable = no-member
# pylint: disable = missing-docstring
# pylint: disable = global-statement
# pylint: disable = pointless-statement

import socket               # Import socket module
import Message_pb2



MID = 0
def main():

    sock = socket.socket()         # Create a socket object

    port = 12347                # Reserve a port for your service.

    sock.connect(("localhost", port))

    while True:

        query = raw_input("Client>>")

        query = query.strip()
        global MID
        objtoser = Message_pb2.Message()

        objtoser.header.uid = MID

        MID = MID+1
        objtoser.header.type = 0
        objtoser.command = query

        sobj = objtoser.SerializeToString()

        sock.send(sobj)

        if query == "exit":
            break

        while True:

            success = False
            objfromser = Message_pb2.Message()
            ret_val = sock.recv(2046)
            #print ret_val
            objfromser.ParseFromString(ret_val)
            #print "Received Object From Server"+"\n\n"
            #print objfromser


            for i in objfromser.server:

                if i == 0:
                    for line in objfromser.str:
                        print line+"\n"
                elif i == 1:
                    tobj = Message_pb2.Message()
                    tobj.header.uid = MID
                    MID = MID+1
                    tobj.header.type = 1
                    tobj.header.ack = objfromser.header.uid+1

                    for squery in objfromser.str:

                        query = raw_input(squery+": ")
                        query = query.strip()
                        tobj.str.append(query)
                    sobj = tobj.SerializeToString()
                    sock.send(sobj)
                elif i == 2:
                    success = True
                    break

            if success:
                break

    print sock.recv(1024)
    sock.close

if __name__ == '__main__':
    main()
