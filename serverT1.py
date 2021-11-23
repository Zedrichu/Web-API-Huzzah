import machine
import network
import socket

#Create access point as WLAN
ap = network.WLAN (network.AP_IF)
#Make the AP active
ap.active(True)
#Configure essid name of AP
ap.config(essid = 'ESP-Group30')
#Configure password of AP
ap.config (authmode = 3, password = 'letmein!')

#Selects a list of board pins
pins = [machine.Pin(i, machine.Pin.IN) for i in (0,2,4,5,12,13,14,15,32,21,22,23)]

#HTML page content to be created at clientIP:80
html = """<!DOCTYPE html> 
<html>
    <head> 
        <title> ESP32 Pins </title>  
    </head>
    <body> 
        <h1> ESP32 Pins </h1>
        <table border ="1"> 
            <tr>
                <th> Pin </th>
                <th> Value </th>
            </tr> %s  
        </table> 
    </body>
</html>
"""
#List of sockets that can be created with any IP and port 80
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

#Initializes a socket - new communication endpoint
s = socket.socket()
#Associates the socket to the address and port set above
s.bind(addr)
#The socket starts listening - willingness to accept connections
s.listen(1)

#Message on screen
print('Listening is on ',addr)
input('Press enter to continue ...')


while True:
    #Blocks the caller until a connection request arrives
    cl, addr = s.accept()
    print('client connected from', addr)
    #Creates a file used as communication client-server
    cl_file = cl.makefile('rwb', 0)
    while True:
        #Checks for the EOF
        line = cl_file.readline()
        print(line)
        if not line or line == b'\r\n':
            break
    #Create rows in the HTML table for each pin and it's value
    rows = ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pins]
    response = html % '\n'.join(rows)
    #Send data over the connection
    cl.send(response)
    #Close the connection
    cl.close()
