# encoding=utf8
import ex_pb2
import sys
import redis

def addmovie(m):

	#m.Name=raw_input("Enter movie name ")
	#m.Actor=raw_input("Enter actor name ")
	#m.Director=raw_input("Enter Director name ")

	m.Name='movie1'
	m.Actor='actor1'
	m.Director='director1'

	m.Duration=43 #int(raw_input("Enter Duration in Minute "))
	str="14/11/1990" #raw_input("Enter Date of Release in DD/MM/YEAR FORMAT ")
	l=str.split('/')
	m.date.day=int(l[0])
	m.date.month=int(l[1])
	m.date.Year=int(l[2])

mov=ex_pb2.Movie()
p=ex_pb2.Movie()

addmovie(mov)

#print mov.Name
#print mov.date.day

s=mov.SerializeToString()
print s
p.ParseFromString(s)

print p

print p.date.day #p.Date.month, p.Date.Year

POOL=redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)

r=redis.Redis(connection_pool=POOL)
r.set('foo','bar')
print r.get('foo')

r.set(mov.Name, s)
print r.get(mov.Name)
p.ParseFromString(r.get(mov.Name))
print p






