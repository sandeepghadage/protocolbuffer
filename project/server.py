#!/usr/bin/python           # This is server.py file
# pylint: disable=no-member
# pylint: disable=missing-docstring
# pylint: disable=global-statement
# pylint: disable=too-many-statements
import datetime
import socket               # Import socket module
import redis
import Message_pb2
import ex_pb2

POOL = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
red = redis.Redis(connection_pool=POOL)
MID = 0

def add_movie(cli, ack):
    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(1)

    objtocli.str.append("Enter Movie Name: ")
    objtocli.str.append("Enter Actors Name separated by commas")
    objtocli.str.append("Enter Directors Name separated by commas")
    objtocli.str.append("Enter Duration in Minute")
    objtocli.str.append("Enter Date of Release in DD/MM/YEAR")
    objtocli.str.append("Select Genre Optioins(one or more)\n"+
                        "Adventure = 0 \n Action = 1 \n Drama = 2 \n Comedy = 3 \n")
    sobj = objtocli.SerializeToString()
    cli.send(sobj)
    objfromcli = Message_pb2.Message()
    objfromcli.ParseFromString(cli.recv(2048))
    print objfromcli
    mobj = ex_pb2.Movie()
    mobj.Name = objfromcli.str[0]
    lst = objfromcli.str[1].split(",")
    for actor in lst:
        actor = actor.strip()
        mobj.Actor.append(actor)

    lst = objfromcli.str[2].split(",")
    for director in lst:
        director = director.strip()
        mobj.Director.append(director)

    mobj.Duration = int(objfromcli.str[3].strip())
    line = objfromcli.str[4]
    line = line.strip()
    lst = line.split("/")
    mobj.date.day = int(lst[0])
    mobj.date.month = int(lst[1])
    mobj.date.Year = int(lst[2])
    lst = (objfromcli.str[5].strip()).split(",")
    for gen in lst:
        gen = gen.strip()
        mobj.genre.append(int(gen))
    name = mobj.Name
    for gen in mobj.genre:         # update genre lists
        if gen == 1:
            red.lpush("Action", name)
        elif gen == 0:
            red.lpush("Adventure", name)

        elif gen == 2:
            red.lpush("Drama", name)

        elif gen == 3:
            red.lpush("Comedy", name)

    smobj = mobj.SerializeToString()
    red.set(mobj.Name, smobj)
    red.lpush("Movies", mobj.Name)
    for actor in mobj.Actor:
        red.lpush(actor, mobj.Name)
    for director in mobj.Director:
        red.lpush(director, mobj.Name)
    del objtocli.server[:]
    del objtocli.str[:]
    objtocli.server.append(2)
    cli.send(objtocli.SerializeToString())


def list_movies(cli, ack):


    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(0)
    objtocli.server.append(2)

    for movie in red.lrange("Movies", 0, -1):
        objtocli.str.append(movie)


    cli.send(objtocli.SerializeToString())

def delete_movie(cli, name, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(0)
    objtocli.server.append(2)

    pipe = red.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        tobj = ex_pb2.Movie()
        tobj.ParseFromString(red.get(name))
        red.lrem("Movies", name, 0)
        for actor in tobj.Actor:
            red.lrem(actor, name, 0)

        for director in tobj.Director:
            red.lrem(director, name, 0)

        for gen in tobj.genre:
            if gen == 1:
                red.lrem("Action", name, 0)

            elif gen == 0:
                red.lrem("Adventure", name, 0)

            elif gen == 2:
                red.lrem("Drama", name, 0)

            elif gen == 3:
                red.lrem("Comedy", name, 0)

        red.delete(name)

        objtocli.str.append("Movie Deleted Successfully")
    else:
        objtocli.str.append("Movie Does not Exist")
    cli.send(objtocli.SerializeToString())


def find_by_actor(cli, name, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(0)
    objtocli.server.append(2)

    pipe = red.pipeline()
    pipe.watch(name)
    if pipe.exists(name):
        for actor in red.lrange(name, 0, -1):
            objtocli.str.append(actor)
    else:
        objtocli.str.append("No Movie For: "+name)

    cli.send(objtocli.SerializeToString())

def find_by_director(cli, name, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(0)
    objtocli.server.append(2)

    pipe = red.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        for actor in red.lrange(name, 0, -1):
            objtocli.str.append(actor)
    else:
        objtocli.str.append("No Movie For: "+name)
    cli.send(objtocli.SerializeToString())

def failure(cli, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID

    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(0)
    objtocli.server.append(2)


    objtocli.str.append("Invalid Command...")

    cli.send(objtocli.SerializeToString())

def setreview(cli, name, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack

    pipe = red.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        objtocli.server.append(1)

        objtocli.str.append("User Name: ")
        objtocli.str.append("Rating: ")
        objtocli.str.append("Comment(Optional): ")

        cli.send(objtocli.SerializeToString())

        #########################################
        objfromcli = Message_pb2.Message()

        objfromcli.ParseFromString(cli.recv(2048))

        mobj = ex_pb2.Movie()
        mobj.ParseFromString(red.get(name))

        rev = ex_pb2.Movie.Review()

        rev.User = objfromcli.str[0]
        rev.Rating = int(objfromcli.str[1])

        director = datetime.datetime.now()

        rev.date.day = director.day
        rev.date.month = director.month
        rev.date.Year = director.year

        if len(objfromcli.str[2]) != 0:
            rev.Comment = objfromcli.str[2]
        else:
            rev.Comment = ""

        mobj.review.extend([rev])
        red.set(name, mobj.SerializeToString())


        #########################################

        objtocli.header.uid = MID
        MID = MID+1
        objtocli.header.type = 1
        objtocli.header.ack = objfromcli.header.uid

        del objtocli.server[:]
        del objtocli.str[:]

        objtocli.str.append("Review Added Successfully")
        objtocli.server.append(0)
        objtocli.server.append(2)

        cli.send(objtocli.SerializeToString())
        #########################################


    else:

        objtocli.server.append(0)
        objtocli.server.append(2)

        objtocli.str.append("No Such a Movie exist..")
        cli.send(objtocli.SerializeToString())

def get_reviews(cli, name, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(0)
    objtocli.server.append(2)

    pipe = red.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        mobj = ex_pb2.Movie()
        mobj.ParseFromString(red.get(name))
        line = "------------------------------------------\n"
        line = line+"UserName  Rating      Date       Comment \n"
        line = line+"------------------------------------------\n"
        objtocli.str.append(line)

        for rev in mobj.review:

            line = rev.User +"        "+ str(rev.Rating)
            line = line +"       "+ str(rev.date.day)
            line = line +"/"+str(rev.date.month)
            line = line +"/"+str(rev.date.Year)
            line = line +"      "+ rev.Comment+"\n"
            objtocli.str.append(line)

    else:
        objtocli.str.append("Movie Does not Exists...")


    cli.send(objtocli.SerializeToString())

def update_movie(cli, name, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    pipe = red.pipeline()
    pipe.watch(name)
    if pipe.exists(name):
        mobj = ex_pb2.Movie()
        mobj.ParseFromString(red.get(name))
        objtocli.str.append("Update Actors Name separated by commas")
        objtocli.str.append("Update Directors Name separated by commas")
        objtocli.str.append("Update Duration in Minute")
        objtocli.str.append("Update Date of Release in DD/MM/YEAR")
        objtocli.server.append(1)

        cli.send(objtocli.SerializeToString())

        ###############################################
        objfromcli = Message_pb2.Message()
        objfromcli.ParseFromString(cli.recv(2048))

        if len(objfromcli.str[0]) > 0:

            for actor in mobj.Actor:          #remove movie from actor list
                red.lrem(actor, name, 0)

            lst = objfromcli.str[0].split(",")

            del mobj.Actor[:]             #delete prev actors

            for actor in lst:                 #update actors in movie obj
                actor = actor.strip()
                mobj.Actor.append(actor)

            for actor in mobj.Actor:         #update movie in actors list
                red.lpush(actor, name)

        if len(objfromcli.str[1]) > 0:

            for director in mobj.Director:          #remove movie from actor list
                red.lrem(director, name, 0)

            lst = objfromcli.str[1].split(",")

            del mobj.Director[:]             #delete prev actors

            for director in lst:                 #update actors in movie obj
                director = director.strip()
                mobj.Director.append(director)

            for director in mobj.Director:         #update movie in actors list
                red.lpush(director, name)

        if len(objfromcli.str[2]) > 0:
            mobj.Duration = int(objfromcli.str[2])

        if len(objfromcli.str[3]) > 0:

            date = objfromcli.str[3].split("/")
            mobj.date.day = int(date[0])
            mobj.date.month = int(date[1])
            mobj.date.Year = int(date[2])
        #############################################

        red.set(name, mobj.SerializeToString())

        objtocli.header.uid = MID
        MID = MID+1
        objtocli.header.ack = objfromcli.header.uid

        del objtocli.str[:]
        del objtocli.server[:]

        objtocli.str.append("Updated Successfully")

    else:
        objtocli.str.append("No such Movie Exist...")
    objtocli.server.append(0)
    objtocli.server.append(2)

    cli.send(objtocli.SerializeToString())


def get_by_genre(cli, name, ack):

    objtocli = Message_pb2.Message()
    global MID
    objtocli.header.uid = MID
    MID = MID+1
    objtocli.header.type = 1
    objtocli.header.ack = ack
    objtocli.server.append(0)
    objtocli.server.append(2)
    pipe = red.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        for actor in red.lrange(name, 0, -1):
            objtocli.str.append(actor)
    else:

        objtocli.str.append("No Movie For: "+name)

    cli.send(objtocli.SerializeToString())



def main():
    sock = socket.socket()         # Create a socket object
    port = 12347                # Reserve a port for your service.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("localhost", port))        # Bind to the port

    sock.listen(5)                 # Now wait for client connection.
    cli, addr = sock.accept()     # Establish connection with client.
    print "Got connection from", addr
    while True:
        objfromcli = Message_pb2.Message()

        objfromcli.ParseFromString(cli.recv(1024))

        print objfromcli

        cmd = objfromcli.command.split(" ")

        if cmd[0] == "newmovie":
            add_movie(cli, objfromcli.header.uid)

        elif cmd[0] == "listmovies":
            list_movies(cli, objfromcli.header.uid)

        elif cmd[0] == "deletemovie":
            delete_movie(cli, cmd[1], objfromcli.header.uid)

        elif cmd[0] == "findbyactor":
            find_by_actor(cli, cmd[1], objfromcli.header.uid)

        elif cmd[0] == "findbydirector":
            find_by_director(cli, cmd[1], objfromcli.header.uid)

        elif cmd[0] == "setreview":
            setreview(cli, cmd[1], objfromcli.header.uid)

        elif cmd[0] == "getreviews":
            get_reviews(cli, cmd[1], objfromcli.header.uid)

        elif cmd[0] == "getbygenre":
            get_by_genre(cli, cmd[1], objfromcli.header.uid)

        elif cmd[0] == "update":
            update_movie(cli, cmd[1], objfromcli.header.uid)

        elif cmd[0] == "exit":
            break

        else:
            failure(cli, objfromcli.header.uid)


    cli.send("Thank you for connecting")
    cli.close()                # Close the connection

if __name__ == '__main__':
    main()
