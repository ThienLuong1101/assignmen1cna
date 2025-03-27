rule 1: make sure you understand the problem => I read the assignment twice and tried to understand all the necesary concept 
before starting it

BASIC WORKFLOW:

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

I have 2 small modifies for the original code:

1/I make this adjustment to verify the cache image. The origin is only read text. 
This adjust ensure the image is cache hit but it will not display the image cuz the point is to cache the data
    cacheFile = open(cacheLocation, "rb")
    cacheData = cacheFile.readlines()
2/cacheLocation = './' + hostname + urllib.parse.quote(resource, safe='/')
to handle special chars like & 

CACHE IMPLEMATION:
 - If the max-age is set to 0, or the response is a 404, or the no-cache/no-store directive is present, 
the server will not cache the response.

 - If the Cache-Control header has a max-age value greater than 0, the response is saved to the cache.
A metadata file is created to store the expiration time of the cache. This tells the server when the cache is no longer valid.

If caching is prohibited, the cache file is deleted (if it exists), and no response is saved.

- 301: If the response is a 301 redirect, the new location (Location: header) is stored, and the redirect response is cached.
- 302: A 302 response is not cached unless specific caching directives are present.
- else Normal responses are cached (assume here in this assignment is 200 OK)
- 500 no consider (not require)


I use .meta file to helps manage cache expiration separately from the cache data. checking the expiration time before serving cached content
in my current implemenation to handle the max-age: 
I extract the time of cache-cache-control max-age and store it into a .meta file to store only expire time of the cached file
-> faster retrieve data. Then, if the request come to proxy I compare the current time with the time in the meta file
if it smaller than the time in meta file -> ok, this cached data can be reused
else the data is exipired, I send the request to the origin server and re-cache the data

the meta file store which is the seconds that have elapsed since January 1, 1970, at 00:00:00 UTC (the Unix epoch).



PROXY BONUS:
1/Check the Expires header of cached objects to determine if a new copy is needed from the origin server instead of just sending back the cached copy 
in my implementation and according to what I understand from RFC: I prioritize the max-age time
which mean if there are max-age and expires header -> take max-age, if it has max-age ignore expire headers
store it to .meta file as it works with max-age

the meta file will contain the seconds until the cache data invalid (max-age or expires header or empty)
if max-age or expires header: the time will check by compare with


2/ observation on pre-fetch:
- Only pre-fetch for text/html content 
- Files are cached but NOT sent to client
- Relative URLs are resolved to absolute URLs
- Errors in pre-fetching do not affect main response

This code checks if the response content is text/html, and if so, it extracts all links (both href and src) 
from the HTML using regular expressions. For each extracted link, it forms the full URL, establishes a socket connection, 
and sends a GET request to pre-fetch the associated resources. The responses are saved in a cache directory.


3/ if there is ':' in the hostname extract the port otherwise set port 80, use valueError to check whether the port valid
