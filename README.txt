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


why the cache image doesn't show cache hit? 
I realize because of the given code structure using text mode 'r'
binary files like images can't be properly read in text mode
using .readlines() expects text content with line breaks

301 will be cached
302 will not be cached only if they have a positive max-age value.

//code logic
if 301 or 302 is found in status line set is_redirect  = True
extract max_age
when max-age = 0 no cache
it should be max-age=0, 404, and 302 no cache? =>

I have 2 small modifies for the original code:

1/I make this adjustment to verify the cache image. The origin is only read text. 
This adjust ensure the image is cache hit but it will not display the image cuz the point is to cache the data
    cacheFile = open(cacheLocation, "rb")
    cacheData = cacheFile.readlines()
2/cacheLocation = './' + hostname + urllib.parse.quote(resource, safe='/')
to handle special chars like & 


I use .meta file to helps manage cache expiration separately from the cache data. checking the expiration time before serving cached content