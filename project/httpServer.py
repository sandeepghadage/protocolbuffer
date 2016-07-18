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

PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser
class myHandler(BaseHTTPRequestHandler):

    #Handler for the GET requests
    def do_GET(self):

        pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
        server = redis.Redis(connection_pool=pool)

        lst = self.path.split(",")
        if lst[0] == "listmovies":

            rply = ""
            for movie in server.lrange("Movies", 0, -1):

                rply = rply+movie+"\n"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rply)

        elif lst[0] == "findbyactor":

            rply = ""
            for movie in server.lrange(lst[1], 0, -1):

                rply = rply+movie+"\n"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rply)

        elif lst[0] == "findbydirector":

            rply = ""
            for movie in server.lrange(lst[1], 0, -1):

                rply = rply+movie+"\n"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rply)

        elif lst[0] == "getreviews":

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(base64.b64encode(server.get(lst[1])))

        elif lst[0] == "findbygenre":


            rply = ""
            for movie in server.lrange(lst[1], 0, -1):

                rply = rply+movie+"\n"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rply)



        return


    def do_POST(self):

        pool = redis.ConnectionPool(host="127.0.0.1", port=6379, db=0)
        server = redis.Redis(connection_pool=pool)

        lss = []
        lss.append(self.path.strip())

        length = int(self.headers.getheader("content-length"))

        lst = self.rfile.read(length).split(",")
        print lst
        lss.append(lst[0])

        if lss[0] == "newmovie":
            lss.append(lst[1])
            print lss[1]
            server.set(lss[1], base64.b64decode(lss[2]))
            server.lpush("Movies", lss[1])

            mobj = ex_pb2.Movie()
            mobj.ParseFromString(base64.b64decode(lss[2]))

            for acotr in mobj.Actor:

                server.lpush(acotr, mobj.Name)

            for director in mobj.Director:

                server.lpush(director, mobj.Name)

            for gen in mobj.genre:

                if gen == 0:
                    server.lpush("Adventure", mobj.Name)
                elif gen == 1:
                    server.lpush("Action", mobj.Name)
                elif gen == 2:
                    server.lpush("Drama", mobj.Name)
                elif gen == 3:
                    server.lpush("Comedy", mobj.Name)


            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write("Successfully Added...")

        elif lss[0] == "deletemovie":

            pipe = server.pipeline()
            pipe.watch(lss[1])

            if pipe.exists(lss[1]):

                mobj = ex_pb2.Movie()
                mobj.ParseFromString(server.get(lss[1]))

                for actor in mobj.Actor:

                    server.lrem(actor, lss[1], 0)

                for director in mobj.Director:

                    server.lrem(director, lss[1], 0)

                for gen in mobj.genre:

                    if gen == 0:
                        server.lrem("Adventure", mobj.Name, 0)
                    elif gen == 1:
                        server.lpush("Action", mobj.Name, 0)
                    elif gen == 2:
                        server.lpush("Drama", mobj.Name, 0)
                    elif gen == 3:
                        server.lpush("Comedy", mobj.Name, 0)


                server.lrem("Movies", lss[1], 0)

                server.delete(lss[1])

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("Successfully Deleted...")

        elif lss[0] == "setreview":

            pipe = server.pipeline()

            pipe.watch(lss[1])

            if pipe.exists(lss[1]):

                mobj = ex_pb2.Movie()

                mobj.ParseFromString(server.get(lss[1]))

                rev = ex_pb2.Movie.Review()

                rev.User = lst[1]

                rev.Rating = int(lst[2])

                rev.Comment = lst[3]

                rev.date.day = int(lst[4])

                rev.date.month = int(lst[5])

                rev.date.Year = int(lst[6])

                mobj.review.extend([rev])

                server.set(lss[1], mobj.SerializeToString())

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("Successfully Added Review...")


        elif "update" in lss[0]:


            mobj = ex_pb2.Movie()

            mobj.ParseFromString(server.get(lss[1]))


            if lss[0] == "updateact":

                for actor in mobj.Actor:

                    server.lrem(actor, lss[1], 0)

                del mobj.Actor[:]

                actors = lst[1:]

                for actor in actors:

                    actor = actor.strip()
                    mobj.Actor.append(actor)
                    server.lpush(actor, lss[1])

                server.set(lss[1], mobj.SerializeToString())
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("Successfully Updated Actors...")

            elif lss[0] == "updatedir":

                for director in mobj.Director:

                    server.lrem(director, lss[1], 0)

                del mobj.Director[:]

                directors = lst[1:]

                for director in directors:

                    director = director.strip()
                    mobj.Director.append(director)
                    server.lpush(director, lss[1])

                server.set(lss[1], mobj.SerializeToString())
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("Successfully Updated Directors...")

            elif lss[0] == "updatedt":

                dte = lst[1].split("/")

                mobj.date.day = int(dte[0])
                mobj.date.month = int(dte[1])
                mobj.date.Year = int(dte[2])

                server.set(lss[1], mobj.SerializeToString())
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("Successfully Updated Date...")


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
