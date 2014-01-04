# MQTT Socket.io Server Bridge for Unity

This is the example node.js code to extract the unity data from the MQTT bus and present in a web application using Socket.io between the server and client.

In this directory is the server.js component that listens on port 3000 using sockets.

In the sub-directory "example_client"  is the example client application that uses this server.

The server.js should not need changing other than bug fixes, extensions of capabilities.

## Pre-requisites

a working node.js environment  

## Installation

In the example_node directory run "npm install ."

## Execution

Start the server - node.server.js

The server listens on port 3000 using websockets.

Start a new shell.  Go to example_client directory.  Follow Readme instructions in that directory.

## Status

1. SOTA implemented but not tested.

## Credits

  - [Jacob Thomas](http://github.com/bjacobt)
  - [Geoff Hollingworth](http://github.com/eusholli)

## License

(The MIT License)

Copyright (c) 2012 Geoff Hollingworth

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
