# Client-side code
import json
from sys import path
from machine import Pin, I2C
# from os import terminal_size
import socket
# Create socket object
# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# address = "192.168.4.1"
# port = 80

# request = b"GET 192.168.4.1:80/pins \r\n"

# #Connect to the board-server
# s.connect ((address, port))
# s.settimeout(2)
# #Send the GET request
# s.send(request)

# #Receive response
# try:
#     response = s.recv(10000)
#     while (len(response)>0):
#         print(response)
#         response = s.recv(10000)
# except:
#     pass

# #Close connection
# s.close()
# #<----------------------------END---------------------->


# Server-side code
# Create the HTML web-site here
html = """<!DOCTYPE html>
<html>

</html>
"""

# On-board code
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Initialize I2C temperature sensor
temp_addr = 24
temp_reg = 5
res_reg = 8

# Function for obtaining temperature from bytearray


def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp


# Call temp_c(data) for computed temperature
# Select pins
pinset = (0, 2, 4, 5, 12, 13, 14, 21, 22, 23, 32)
pins = [Pin(i, Pin.IN) for i in pinset]
pinlist = []
for i in pinset:
    pinlist.append("Pin {}".format(i))

# <----------------On-board code completed----------------->

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

# Associate with the address found
s.bind(addr)
# Await only one request
s.listen(1)
print('Listening is on', addr)

while True:
    # Establish connection
    client, addr = s.accept()
    print('Client connected from', addr)
    cl_file = client.makefile('rwb', 0)
    response = html
    while True:
        line = cl_file.readline()
        # get temperature kinda

        # GET Request is found
        if line.find(b'GET') != -1:
            # Transform to string, go in between GET and HTTP
            # strip() used to remove whitespaces in the path
            respath = str(line).split('GET')[1].split('HTTP')[0].strip()
            pathlist = respath.split('/')
            client.send("HTTP/1.1 200 OK\n")
            if pathlist[1] == '':
                html = """<!DOCTYPE html>
                <html>
                    <head> <title>ESP32 Pins</title> </head>
                    <body> <h1>ESP32 Pins</h1>
                        <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
                    </body>
                </html>
                """
                rows = ['<tr><td>%s</td><td>%d</td></tr>' %
                        (str(p), p.value()) for p in pins]
                response = html % '\n'.join(rows)
                client.send("Content-Type: text/html\n")

            elif (pathlist[1] == 'sensors'):
                if len(pathlist) == 2:
                    response = json.dumps(
                        [
                            "temperature",
                            "button",
                            "potentiometer"
                        ])
                elif pathlist[2] == 'temperature':
                    try:
                        i2c = I2C(scl=Pin(22), sda=Pin(23))
                        data = bytearray(2)
                        i2c.readfrom_mem_into(temp_addr, temp_reg, data)
                        response = json.dumps(
                            {"name": "temperature", "value": temp_c(data)})
                    except:
                        response = json.dumps(
                            {"error": "Temperature sensor not connected."})

                elif pathlist[2] == 'button':
                    try:

                        response = json.dumps(
                            {"name": "button", "value": button.value()})
                    except:
                        response = json.dumps(
                            {"error": "Button not connected."})
                elif pathlist[2] == 'potentiometer':
                    try:
                        response = json.dumps(
                            {"name": "potentiometer", "value": adc.read()})
                    except:
                        response = json.dumps(
                            {"error": "Potentiometer not connected."})
                else:
                    response = json.dumps(
                        {"error": "No such sensor exists."})

            elif pathlist[1] == 'pins':
                if len(pathlist) == 2:
                    response = json.dumps(pinlist)
                else:
                    no = int(pathlist[2].split('pin')[-1])
                    pinname = "Pin {}".format(no)
                    try:
                        val = pins[pinset.index(no)].value()
                        response = json.dumps(
                            {"name": pinname, "value": val})
                    except:
                        response = json.dumps(
                            {"error": "No such pin exists."})

            # elif pathlist[1]=='/toggle':
        # POST Request is found
        # elif line.find(b'POST')!=-1:
        # DELETE Request is found
        # elif line.find(b'DELETE')!=-1:
        if not line or line == b'\r\n':
            break
    if len(pathlist[1]) > 1:
        client.send("Content-Type: application/json\n")
    client.send("\n"+response)
    client.close()
