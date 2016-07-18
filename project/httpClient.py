# pylint: disable  =  no-member
# pylint: disable  =  missing-docstring
# pylint: disable  =  global-statement
# pylint: disable  =  too-many-statements
import httplib
import datetime
import base64
import ex_pb2

#print(r1.status,  r1.reason)

def find_movie(httpconn, name):

    httpconn.request("GET", "listmovies")

    request = httpconn.getresponse()

    data = request.read().split("\n")

    for movie in data:
        if movie == name:
            return 1

    return 0

def add_movie(httpconn):

    objtoser = ex_pb2.Movie()

    objtoser.Name = (raw_input("Enter Movie Name: ").strip())

    if find_movie(httpconn, objtoser.Name) == 1:
        print "Movie Already Exists"
        return

    line = raw_input("Enter Actors separated by commas :")

    lst = line.strip().split(",")

    for actor in lst:
        actor = actor.strip()
        objtoser.Actor.append(actor)


    line = raw_input("Enter Directors separated by commas :")

    lst = line.strip().split(",")

    for director in lst:
        director = director.strip()
        objtoser.Director.append(director)



    objtoser.Duration = int(raw_input("Enter Duration in Minutes: "))

    line = raw_input("Enter Date of Release in DD/MM/YY Format: ")
    line = line.strip()
    lst = line.split("/")
    objtoser.date.day = int(lst[0])
    objtoser.date.month = int(lst[1])
    objtoser.date.Year = int(lst[2])




    line = raw_input("Select Genre Options(one or more) separated by commas "+'\n'
                     +'Adventure = 0'+'\nAction = 1'+'\nDrama = 2'+'\nComedy = 3'+'\n')

    lst = line.strip().split(",")

    for gen in lst:
        gen = gen.strip()
        objtoser.genre.append(int(gen))

    httpconn.request("POST", "newmovie", objtoser.Name+","
    	                +base64.b64encode(objtoser.SerializeToString()))

    request = httpconn.getresponse()

    data = request.read()

    print data

def list_movie(httpconn):

    httpconn.request("GET", "listmovies")

    request = httpconn.getresponse()

    data = request.read().split("\n")

    for movie in data:
        print movie


def find_by_actor(httpconn, name):

    httpconn.request("GET", "findbyactor,"+name)

    request = httpconn.getresponse()

    data = request.read()

    print data


def find_by_director(httpconn, name):

    httpconn.request("GET", "findbydirector,"+name)

    request = httpconn.getresponse()

    data = request.read()

    print data


def set_review(httpconn, name):


    if find_movie(httpconn, name) == 0:
        print "Movie does not exists"
        return

    rply = raw_input("Enter User Name: ").strip()

    rply = rply+", "

    rply = rply+raw_input("Enter Rating: ").strip()

    rply = rply+", "

    rply = rply+raw_input("Commnet: ").strip()

    rply = rply+", "

    now = datetime.datetime.now()

    rply = rply+str(now.day)+", "+str(now.month)+","+str(now.year)

    httpconn.request("POST", "setreview", name+","+rply)

    request = httpconn.getresponse()

    data = request.read()

    print data

def get_reviews(httpconn, name):


    if find_movie(httpconn, name) == 0:
        print "Movie does not exists"
        return
    httpconn.request("GET", "getreviews,"+name)

    request = httpconn.getresponse()

    data = request.read()

    mobj = ex_pb2.Movie()

    mobj.ParseFromString(base64.b64decode(data))

    print "----------------------------------------\n"
    print " User   	Date      Rating     Comments \n"
    print"------------------------------------------\n"

    for rev in mobj.review:

        dte = str(rev.date.day)+"/"+str(rev.date.month)+"/"+str(rev.date.Year)
        print rev.User+"      "+dte+"       "+str(rev.Rating)+"      "+rev.Comment+"\n"


def find_by_genre(httpconn, name):

    httpconn.request("GET", "findbygenre,"+name)

    request = httpconn.getresponse()

    data = request.read()

    print data


def update(httpconn, name):

    if find_movie(httpconn, name) == 0:
        print "Movie does not exists"
        return

    print "Select One of the Following Option: \n"
    print "update Actors (Press 0)\nupdate Director(Press 1)"
    print "update DateofRelease (Press 2)\n:"

    opt = int(raw_input(""))

    if opt == 0:

        rply = raw_input("Enter Actors Separated by Commas :").strip()

        httpconn.request("POST", "updateact", name+","+rply)

    elif opt == 1:

        rply = raw_input("Enter Directors Separated by Commas :").strip()

        httpconn.request("POST", "updatedir", name+","+rply)

    elif opt == 2:

        rply = raw_input("Enter Date in DD/MM/YY Format: ")

        httpconn.request("POST", "updatedt", name+","+rply)

    else:
        print "Invalid Option...."
        return

    request = httpconn.getresponse()

    data = request.read()

    print data




def delete_movie(httpconn, name):

    if find_movie(httpconn, name) == 0:
        print "Movie does not exists"
        return

    httpconn.request("POST", "deletemovie", name)

    request = httpconn.getresponse()

    data = request.read()

    print data


def main():

    httpconn = httplib.HTTPConnection("localhost:8080")

    while True:

        line = raw_input("Client>>")
        query = line.strip().split(" ")

        if query[0] == "newmovie":
            add_movie(httpconn)

        elif query[0] == "listmovies":
            list_movie(httpconn)

        elif query[0] == "findbyactor":
            find_by_actor(httpconn, query[1])

        elif query[0] == "findbydirector":
            find_by_director(httpconn, query[1])

        elif query[0] == "deletemovie":
            delete_movie(httpconn, query[1])

        elif query[0] == "setreview":
            set_review(httpconn, query[1])

        elif query[0] == "getreviews":
            get_reviews(httpconn, query[1])

        elif query[0] == "findbygenre":
            find_by_genre(httpconn, query[1])

        elif query[0] == "update":
            update(httpconn, query[1])

        elif query[0] == "exit":
            break

        else:
            print "Invalid Command...."

    httpconn.close()

if __name__ == '__main__':
    main()
