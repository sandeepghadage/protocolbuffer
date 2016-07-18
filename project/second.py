"""protobuf example"""
# pylint: disable=no-member
# pylint: disable=missing-docstring
import sys
import datetime
import redis
import ex_pb2

def addmovie(server):
    mobj = ex_pb2.Movie()
    mobj.Name = raw_input("Enter Movie Name: ").strip()
    mobj.Name = mobj.Name.strip()
    print "Enter Actors Name separated by commas: "
    actors = raw_input("").strip()
    lstr = actors.split(",")
    for actor in lstr:
        actor = actor.strip()
        mobj.Actor.append(actor)
    print "Enter Directors Name Separated by commas: "
    directors = raw_input("").strip()
    lstr = directors.split(",")
    for director in lstr:
        director = director.strip()
        mobj.Director.append(director)
    mobj.Duration = int(raw_input("Enter Duration in Minute ").strip())
    strr = raw_input("Enter Date of Release in DD/MM/YEAR FORMAT ").strip()
    lstr = strr.split("/")
    mobj.date.day = int(lstr[0])
    mobj.date.month = int(lstr[1])
    mobj.date.Year = int(lstr[2])
    print "\nSelect Genre Options Separated by commas:"+"\n"
    print "Adventure = 0"+"\nAction = 1"+"\nDrama = 2"+"\nComedy = 3"+"\n"
    inputs = raw_input("").strip()
    for opt in inputs.split(","):
        opt = opt.strip()
        mobj.genre.append(int(opt))
        if int(opt) == 0:
            server.lpush("Adventure", mobj.Name)
        elif int(opt) == 1:
            server.lpush("Action", mobj.Name)
        elif int(opt) == 2:
            server.lpush("Drama", mobj.Name)
        elif int(opt) == 3:
            server.lpush("Comedy", mobj.Name)

    sobj = mobj.SerializeToString()
    server.set(mobj.Name, sobj)
    server.lpush("Movies", mobj.Name)
    for actor in mobj.Actor:
        server.lpush(actor, mobj.Name)
    for actor in mobj.Director:
        server.lpush(actor, mobj.Name)


def get_movie(server, name):

    mov = ex_pb2.Movie()
    with server.pipeline() as pipe:
        pipe.watch(name)
        if pipe.exists(name):
            print "exist"
            mov.ParseFromString(pipe.get(name))
            print mov
        else:
            print "not exist"

def list_movies(server):

    for key in server.lrange("Movies", 0, -1):#.sort():

        print key+"\n"

def delete_movie(server, name):

    with server.pipeline() as pipe:
        pipe.watch(name)
        if pipe.exists(name):
            mov = ex_pb2.Movie()
            mov.ParseFromString(pipe.get(name))
            for actor in mov.Actor:
                server.lrem(actor, name, 0)
            server.lrem("Movies", name, 0)
            for director in mov.Director:
                server.lrem(director, name, 0)

            for gen in mov.genre:

                if gen == 0:
                    server.lrem("Adventure", name, 0)
                elif gen == 1:
                    server.lrem("Action", name, 0)
                elif gen == 2:
                    server.lrem("Drama", name, 0)
                elif gen == 3:
                    server.lrem("Comedy", name, 0)

            server.delete(name)
            print "deleted successfully"+"\n"

        else:
            print "does not exist"+"\n"

def find_act_or_dir(server, name):

    for movie in server.lrange(name, 0, -1):

        print movie+"\n"

def get_reviews(server, name):

    pipe = server.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        mov = ex_pb2.Movie()
        mov.ParseFromString(pipe.get(name))

        print "---------------------------------------------------------"
        print "User           Rating            Date            Comment  "
        print "---------------------------------------------------------\n"
        for rev in mov.review:

            print rev.User+"           "+str(rev.Rating)+"          ",
            print str(rev.date.day)+"/"+str(rev.date.month)+"/"+str(rev.date.Year)+"         ",
            print rev.Comment+"\n"

    else:

        print "no such a movie exist"


def set_review(server, name):

    pipe = server.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        mobj = ex_pb2.Movie()
        mobj.ParseFromString(server.get(name))

        rev = ex_pb2.Movie.Review()

        rev.User = raw_input("User Name: ").strip()
        rev.Rating = int(raw_input("Enter Rating: ").strip())

        dte = datetime.datetime.now()

        rev.date.day = dte.day
        rev.date.month = dte.month
        rev.date.Year = dte.year

        rev.Comment = raw_input("Comment: ").strip()

        mobj.review.extend([rev])



        server.set(name, mobj.SerializeToString())

        print "Review Added Successfully.....\n "

    else:

        print "Movie does not exists...."


def find_by_genre(server, name):

    for gen in server.lrange(name, 0, -1):

        print gen+"\n"


def update_movie(server, name):

    pipe = server.pipeline()
    pipe.watch(name)
    if pipe.exists(name):

        mobj = ex_pb2.Movie()

        mobj.ParseFromString(server.get(name))

        line = raw_input("Update Actors Separated by Commas: ").strip()

        if len(line) > 0:

            for actor in mobj.Actor:

                server.lrem(actor, name, 0)

            del mobj.Actor[:]

            for actor in line.split(", "):

                actor = actor.strip()
                mobj.Actor.append(actor)
                server.lpush(actor, name)

        line = raw_input("Update Directors Separated by Commas: ").strip()

        if len(line) > 0:

            for director in mobj.Director:

                server.lrem(director, name, 0)

            del mobj.Director[:]

            for director in line.split(", "):

                director = director.strip()
                mobj.Director.append(director)
                server.lpush(director, name)

        line = raw_input("Update Date of Release in DD/MM/YY Format: ").strip()
        if len(line) > 0:

            dte = line.split("/")
            mobj.date.day = int(dte[0])
            mobj.date.month = int(dte[1])
            mobj.date.Year = int(dte[2])

        server.set(name, mobj.SerializeToString())
        print "Movie Updated Successfully...."
    else:

        print "Movie does not exist...."


def main():

    arl = sys.argv

    pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
    server = redis.Redis(connection_pool=pool)

    if arl[1] == "newmovie":
        addmovie(server)

    elif arl[1] == "getmovie":
        get_movie(server, arl[2])

    elif arl[1] == "listmovies":
        list_movies(server)

    elif arl[1] == "deletemovie":
        delete_movie(server, arl[2])

    elif arl[1] == "findbyactor" or arl[1] == "findbydirector":
        find_act_or_dir(server, arl[2])

    elif arl[1] == "getreviews":
        get_reviews(server, arl[2])

    elif arl[1] == "setreview":
        set_review(server, arl[2])

    elif arl[1] == "findbygenre":
        find_by_genre(server, arl[2])

    elif arl[1] == "update":
        update_movie(server, arl[2])

if __name__ == "__main__":
    main()
