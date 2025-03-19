rule 1: make sure you understand the problem => I read the assignment twice and tried to understand all the necesary concept 
before starting it

So, The first thing first I need to set up a server socket, bind, and listen
the socket will use IPv4 addresses and TCP for communication
bind it on given host and port
next the socket need to start listening for incoming connections
arg 5 specifies the backlog (max num of queued connections) more than 5 -> reject

get GET HTTP request from client: It reads up to BUFFER_SIZE bytes of data sent by the client and stores it in the variable message_bytes
ok now I need to check if the cache hit with that request or not
if yes, I concatinates cached data into response string send them to client
The encode() method is used to convert the string response into bytes, as the sendall() method expects a byte-like object.
if no, create a new socket to connect to origin server using a resolved IP address and port 80

the first line of http request contains: method, resource, version
http/1.1 requires hostname so I need to provide that and the connection should be closed after the server sends the response.


GET THE REPONSE FROM ORIGIN server
ok I need a byte string to store variable in byte
make it receive data until no more data -> using while loop
store them to the variable

send them all to the client
write the response to cachefile for future request

//this one so far handles a normal 200 GET request first request to origin server second cache work
next time
work on redirect request, bad request (shouldn't cache), max-age
