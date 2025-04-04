# Include the libraries for socket and system calls
import socket
import sys
import os
import argparse
import re
import time
import urllib.parse
import email.utils
from datetime import datetime, timezone
# 1MB buffer size
BUFFER_SIZE = 1000000

# Get the IP address and Port number to use for this web proxy server
parser = argparse.ArgumentParser()
parser.add_argument('hostname', help='the IP Address Of Proxy Server')
parser.add_argument('port', help='the port number of the proxy server')
args = parser.parse_args()
proxyHost = args.hostname
proxyPort = int(args.port)

# Create a server socket, bind it to a port and start listening
try:
  # Create a server socket
  # ~~~~ INSERT CODE ~~~~
  serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # ~~~~ END CODE INSERT ~~~~
  print ('Created socket')
except:
  print ('Failed to create socket')
  sys.exit()

try:
  # Bind the the server socket to a host and port
  # ~~~~ INSERT CODE ~~~~
  serverSocket.bind((proxyHost, proxyPort))
  # ~~~~ END CODE INSERT ~~~~
  print ('Port is bound')
except:
  print('Port is already in use')
  sys.exit()

try:
  # Listen on the server socket
  # ~~~~ INSERT CODE ~~~~
  serverSocket.listen(5) # max of 5 connections
  # ~~~~ END CODE INSERT ~~~~
  print ('Listening to socket')
except:
  print ('Failed to listen')
  sys.exit()

# continuously accept connections
while True:
  print ('Waiting for connection...')
  clientSocket = None

  # Accept connection from client and store in the clientSocket
  try:
    # ~~~~ INSERT CODE ~~~~
    clientSocket, addr = serverSocket.accept()
    # ~~~~ END CODE INSERT ~~~~
    print ('Received a connection')
  except:
    print ('Failed to accept connection')
    sys.exit()

  # Get HTTP request from client
  # and store it in the variable: message_bytes
  # ~~~~ INSERT CODE ~~~~
  message_bytes = clientSocket.recv(BUFFER_SIZE)
  # ~~~~ END CODE INSERT ~~~~
  message = message_bytes.decode('utf-8')
  print ('Received request:')
  print ('< ' + message)

  # Extract the method, URI and version of the HTTP client request 
  requestParts = message.split()
  method = requestParts[0]
  URI = requestParts[1]
  version = requestParts[2]

  print ('Method:\t\t' + method)
  print ('URI:\t\t' + URI)
  print ('Version:\t' + version)
  print ('')

  # Get the requested resource from URI
  # Remove http protocol from the URI
  URI = re.sub('^(/?)http(s?)://', '', URI, count=1)

  # Remove parent directory changes - security
  URI = URI.replace('/..', '')

  # Split hostname from resource name
  resourceParts = URI.split('/', 1)
  hostname = resourceParts[0]
  resource = '/'

  if len(resourceParts) == 2:
    # Resource is absolute URI with hostname and resource
    resource = resource + resourceParts[1]

  print ('Requested Resource:\t' + resource)

  # Check if resource is in cache
  try:
    cacheLocation = './' + hostname + resource
    cacheLocation = './' + hostname + urllib.parse.quote(resource, safe='/')
    if cacheLocation.endswith('/'):
        cacheLocation = cacheLocation + 'default'

    print ('Cache location:\t\t' + cacheLocation)

    fileExists = os.path.isfile(cacheLocation)
    
    # Check wether the file is currently in the cache
    cacheFile = open(cacheLocation, "rb")
    cacheData = cacheFile.readlines()

    print ('Cache hit! Loading from cache file: ' + cacheLocation)
    # ProxyServer finds a cache hit
    # Send back response to client 
    # ~~~~ INSERT CODE ~~~~
    #check the meta file for the time
    #this meta file will contain the time of max-age or Expires header
    #the time of max-age is prioritized
    metaPath = cacheLocation + '.meta'
    if os.path.isfile(metaPath):
        with open(metaPath, 'r') as metaFile:
            try:
                expiration_time = int(metaFile.read().strip())
                current_time = int(time.time())
                
                #expire
                if current_time > expiration_time:
                    print('Cache entry expired. Need to fetch fresh content.')
                    raise Exception("Cache expired")
                # the time is still ok
                else:
                    print(f'Cache valid until: {time.ctime(expiration_time)}')
            except:
                print('Invalid metadata file or expired cache. Treating as cache miss.')
                raise Exception("Invalid metadata or expired")

    # If we get here, either there's no max-age constraint or the cache is still valid
    response = ""
    for line in cacheData:
        response += line
    clientSocket.sendall(response.encode())
    # ~~~~ END CODE INSERT ~~~~
    cacheFile.close()
    print ('Sent to the client:')
    print ('> ' + cacheData)
  except:
    # cache miss.  Get resource from origin server
    originServerSocket = None
    # Create a socket to connect to origin server
    # and store in originServerSocket
    # ~~~~ INSERT CODE ~~~~
    originServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ~~~~ END CODE INSERT ~~~~

    print ('Connecting to:\t\t' + hostname + '\n')
    try:
      # Get the IP address for a hostname
      address = socket.gethostbyname(hostname)
      # Connect to the origin server
      # ~~~~ INSERT CODE ~~~~
      port = 80
      if ':' in hostname:
          try:
              hostname, port = hostname.split(':')
              port = int(port)
          except ValueError:
              print('Invalid port specified. Defaulting to 80')
              port = 80
      originServerSocket.connect((address, port))
      # ~~~~ END CODE INSERT ~~~~
      print(f'Connected to origin Server at {address}:{port}')

      originServerRequest = ''
      originServerRequestHeader = ''
      # Create origin server request line and headers to send
      # and store in originServerRequestHeader and originServerRequest
      # originServerRequest is the first line in the request and
      # originServerRequestHeader is the second line in the request
      # ~~~~ INSERT CODE ~~~~
      originServerRequest = f"{method} {resource} HTTP/1.1"
      originServerRequestHeader = f"Host: {hostname}\r\nConnection: close"
      # ~~~~ END CODE INSERT ~~~~

      # Construct the request to send to the origin server
      request = originServerRequest + '\r\n' + originServerRequestHeader + '\r\n\r\n'

      # Request the web resource from origin server
      print ('Forwarding request to origin server:')
      for line in request.split('\r\n'):
        print ('> ' + line)

      try:
        originServerSocket.sendall(request.encode())
      except socket.error:
        print ('Forward request to origin failed')
        sys.exit()

      print('Request sent to origin server\n')

      # Get the response from the origin server
      # ~~~~ INSERT CODE ~~~~
      response_bytes = b""
      while True:
        data = originServerSocket.recv(BUFFER_SIZE)
        if not data:
            break
        response_bytes += data
      # ~~~~ END CODE INSERT ~~~~

      # Send the response to the client
      # ~~~~ INSERT CODE ~~~~
      clientSocket.sendall(response_bytes)
      # ~~~~ END CODE INSERT ~~~~

      # Create a new file in the cache for the requested file.
      cacheDir, file = os.path.split(cacheLocation)
      print ('cached directory ' + cacheDir)
      if not os.path.exists(cacheDir):
        os.makedirs(cacheDir)
      cacheFile = open(cacheLocation, 'wb')

      # Save origin server response in the cache file
      # ~~~~ INSERT CODE ~~~~
      is_redirect = False
      is_404 = False
      status_line = response_bytes.split(b'\n', 1)[0].decode('utf-8', 'ignore')
      if ' 301 ' in status_line or ' 302 ' in status_line:
          is_redirect = True
      elif ' 404 ' in status_line:
          is_404 = True

      # Extract headers and cache-control info
      headers = response_bytes.split(b'\r\n\r\n', 1)[0].decode('utf-8', 'ignore')
      cache_control = re.search(r'Cache-Control:.*?(max-age=([0-9]+))', headers, re.IGNORECASE)
      max_age_zero = cache_control and int(cache_control.group(2)) == 0
      no_cache = re.search(r'Cache-Control:.*?(no-cache|no-store)', headers, re.IGNORECASE)
      expires = re.search(r'Expires:.*', headers, re.IGNORECASE)
        
      # max-age = 0 or 404 not found or no-store -> no cache
      if max_age_zero or is_404 or no_cache:
          if max_age_zero:
            print('Cache-Control prohibits caching (max-age=0). Not caching.')
          elif is_404:
            print('Cache-Control prohibits caching (404 not found). Not caching.')
          elif no_cache:  
            print('Cache-Control specifies no-store. Not caching.')
          cacheFile.close()
          if os.path.exists(cacheLocation):
              os.remove(cacheLocation)

      # If Cache-Control specifies a max-age, use it for caching
      elif cache_control and int(cache_control.group(2)) > 0:
          max_age = int(cache_control.group(2))
          expiration_time = int(time.time()) + max_age
          
          # Cache the response if it has a positive max-age
          cacheFile.write(response_bytes)
          
          # Create metadata file with expiration time
          with open(cacheLocation + '.meta', 'w') as metaFile:
              metaFile.write(str(expiration_time))
          
          print(f'Cached with max-age={max_age} seconds, expires at: {time.ctime(expiration_time)}')
      #handle expires
      # Check if the Expires header is present
      elif expires:
          # Parse the Expires header to a datetime object
          expires_time = email.utils.parsedate_to_datetime(expires.group(1))
          
          # Get the current UTC time
          current_time = datetime.now(timezone.utc)

          # Calculate the expiration time by adding the difference (in seconds) between Expires time and current time
          stored_time = int(time.time()) + int((expires_time - current_time).total_seconds())

          cacheFile.write(response_bytes)

          # Create metadata file with expiration time
          with open(cacheLocation + '.meta', 'w') as metaFile:
              metaFile.write(str(stored_time))
      # Handle 301 redirects with proper cache handling
      elif ' 301 ' in status_line:
          # Cache the 301 redirect response
          if 'Location:' in headers:
              location_match = re.search(r'Location: (.+)', headers, re.IGNORECASE)
              if location_match:
                  redirect_url = location_match.group(1)
                  print(f'Cashing 301 redirect to: {redirect_url}')
          
          # Write the response to cache
          cacheFile.write(response_bytes)
          print('Cached 301 redirect response')

      # Handle 302 redirects with cache consideration
      elif ' 302 ' in status_line:
          print('Not caching 302 response without caching directives.')
          cacheFile.close()
          if os.path.exists(cacheLocation):
              os.remove(cacheLocation)
      # normal cache for the other requests
      else:
        #pre-fetch for text/html
        if 'text/html' in headers.lower():
          print("pre-fetch occurs")
          #parse the html and store the href and src in a set list avoid duplicate
          html = response_bytes.decode('utf-8', 'ignore') # Decode HTML response
          links = list(set(re.findall(r'(?:href|src)="([^"]+)"', html)))
          base_url = f"http://{hostname}"
          for link in links:
            # Join the base URL with the relative link to get the full URL
            url = urllib.parse.urljoin(base_url, link)
            try:
                #make GET request for the resource
                host, path = urllib.parse.urlparse(url).hostname, urllib.parse.urlparse(url).path
                sock = socket.create_connection((host, 80))
                request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                sock.send(request.encode())
                response = sock.recv(4096) # Receive the response (up to 4096 bytes)
                
                # Cache response
                filepath = f"./cache/{host}{path}"
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'wb') as file:
                    file.write(response)
                sock.close()
            except Exception as e:
                print(f"Failed to pre-fetch {url}: {e}")

        cacheFile.write(response_bytes)
        print('cache response')

      
      # ~~~~ END CODE INSERT ~~~~
      cacheFile.close()
      print ('cache file closed')

      # finished communicating with origin server - shutdown socket writes
      print ('origin response received. Closing sockets')
      originServerSocket.close()
       
      clientSocket.shutdown(socket.SHUT_WR)
      print ('client socket shutdown for writing')
    except OSError as err:
      print ('origin server request failed. ' + err.strerror)

  try:
    clientSocket.close()
  except:
    print ('Failed to close client socket')
