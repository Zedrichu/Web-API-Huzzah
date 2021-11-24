import machine
import socket

button = machine.Pin(14,machine.Pin.IN,machine.Pin.PULL_UP)

#Initialize I2C temperature sensor
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(23))
address = 24
temp_reg = 5
res_reg = 8

#Function for obtaining temperature from bytearray
def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp

#Initialization of temperatures for range
data = bytearray(2)
i2c.readfrom_mem_into(address, temp_reg, data)
t0 = temp_c(data)
th = 31

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
        if not line or line == b'\r\n':
            break
    #Create rows in the HTML table for each pin and it's value
    rows = ['<tr><td>%s</td><td>%d</td></tr>' % (str(p), p.value()) for p in pins]
    rows.append('<tr><td>%s</td><td>%d</td></tr>' % ("Button value",button.value()))
    data = bytearray(2)
    i2c.readfrom_mem_into(address, temp_reg, data)
    rows.append = ('<tr><td>%s</td><td>%d</td></tr>' % ("Temperature",temp_c(data)))
    response = html % '\n'.join(rows)
    #Send data over the connection
    cl.send(response)
    #Close the connection
    cl.close()
