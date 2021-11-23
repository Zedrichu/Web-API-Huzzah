#Client-side code
from os import terminal_size
import socket 
#Create socket object
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

address = "192.168.4.1"
port = 80

request = b"GET 192.168.4.1:80/pins \r\n"

#Connect to the board-server
s.connect ((address, port))
s.settimeout(2)
#Send the GET request
s.send(request)

#Receive response
try:
    response = s.recv(10000)
    while (len(response)>0):
        print(response)
        response = s.recv(10000)
except:
    pass

#Close connection
s.close()
#<----------------------------END---------------------->



#Server-side code
#Create the HTML web-site here
html = """<!DOCTYPE html>
<html>

</html>
"""

#On-board code
from machine import Pin, I2C, ADC
button = Pin(14,Pin.IN,Pin.PULL_UP)

#Initialize Analog-Digital Converter 
adc = ADC(Pin(32))
adc.width(ADC.WIDTH_12BIT)
adc.atten(ADC.ATTN_11DB)

#Initialize I2C temperature sensor
i2c = I2C(scl=Pin(22), sda=Pin(23))
temp_addr = 24
temp_reg = 5
res_reg = 8

#Function for obtaining temperature from bytearray
def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp

data = bytearray(2)
i2c.readfrom_mem_into(temp_addr, temp_reg, data)
#Call temp_c(data) for computed temperature
#Select pins
pinset = (0,2,4,5,12,13,14,21,22,23,32) 
pins = [Pin(i, Pin.IN) for i in pinset]
pinlist = []
for i in pinset:
    pinlist.append("\"pin{}\"".format(i))                    
                    
#<----------------On-board code completed----------------->

import socket 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = socket.getaddrinfo('0.0.0.0',80)[0][-1]

#Associate with the address found
s.bind(addr)
#Await only one request 
s.listen(1) 
print('Listening is on',addr)
import json

while True:
    #Establish connection
    client, addr = s.accept()
    print('Client connected from',addr)    
    cl_file = client.makefile('rwb',0)
    while True:
        line = cl_file.readline()
        #GET Request is found
        if line.find(b'GET')!=-1:
            #Transform to string, go in between GET and HTTP
            #strip() used to remove whitespaces in the path
            respath = str(line).split('GET')[1].split('HTTP')[0].strip()
            pathlist = respath.split('/')
            if pathlist[1]=='sensors':
                if len(pathlist)==2:
                    response = json.dumps(
                        [
                            "temperature",
                            "button",
                            "potentiometer"
                        ])
                elif pathlist[2]=='temperature':
                    data = bytearray(2)
                    i2c.readfrom_mem_into(temp_addr, temp_reg, data)
                    response = json.dumps({"temperature":temp_c(data)})
                elif pathlist[2]=='button':
                    response = json.dumps({"button":button.value()})
                else:
                    response = json.dumps({"potentiometer":adc.read()})
                            
            elif pathlist[1]=='/pins':
                if len(pathlist)==2:
                    response = json.dumps(pinlist)
                else:
                    no = int(pathlist[2][-1])
                    pinname = pathlist[2]
                    val = pins[pinset.index(no)]
                    response = json.dumps({pinname:val})
            #elif pathlist[1]=='/toggle':    
        #POST Request is found    
        #elif line.find(b'POST')!=-1:
        #DELETE Request is found
        #elif line.find(b'DELETE')!=-1:
        #PATCH Request is found
        #elif line.find(b'PATCH')!=-1:
        if not line or line==b'\r\n':
            break
    client.send(response)
    client.close()