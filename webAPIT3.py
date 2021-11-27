#WEB API for Huzzah32 board

# Server-side code
import json
from sys import path
from machine import Pin, I2C, ADC
import neopixel
# from os import terminal_size
import socket
# Create the HTML web-site here
html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
  	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  	<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
  	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
    <title>IoT Node Feather Huzzah32</title>
</head>
<body style="background-color: 	#170000; text-align: center;">

    <nav class="navbar navbar-expand-sm bg-warning navbar-light sticky-top">
        <a class="navbar-brand" href="#">Huzzah32 Board</a>
    
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#collapsibleNavbar">
            <span class="navbar-toggler-icon"></span>
        </button>
    
        <div class="collapse navbar-collapse" id="collapsibleNavbar">
            <ul class="navbar-nav">
                <li class="nav-item active">
                    <a class="nav-link" href="http://192.168.4.1:80/sensors">Pins</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="http://192.168.4.1:80/pins">Sensors</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link disabled" href="#">Neo-Pixel</a>
                </li>
            </ul>
        </div>
    
        <form class="form-inline" action="/action_page.php">
            <input class="form-control mr-sm-2" type="text" placeholder="Search">
            <button class="btn btn-success" type="submit">Search</button>
        </form>
    </nav>
    
    
    
    <h1 style="margin-bottom: 50px; color:bisque">Webpage of Feather Huzzah32 (Group 30)</h1>
    <div>
        <h4 style="color:bisque">View JSON of all devices connected to the board</h4>
        <a href="http://192.168.4.1:80/sensors" class="btn btn-primary" role="button">View sensors JSON</a>
        <a href="http://192.168.4.1:80/pins" class="btn btn-success" role="button">View pins JSON</a>
    </div>
    
    <div class="btn-group-vertical">
        <h4 style="color:bisque">View JSON of selected device or pin </h4>
        <div class="btn-group">
            <button type="button" class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
				Sensors
			</button>
			<div class="dropdown-menu">
				<a class="dropdown-item" href="http://192.168.4.1:80/sensors/temperature">Temperature Sensor</a>
                <a class="dropdown-item" href="http://192.168.4.1:80/sensors/button">Button</a>
                <a class="dropdown-item" href="http://192.168.4.1:80/sensors/potentiometer">Potentiometer</a>
            </div>
        </div>
        <div class="btn-group">
            <button type="button" class="btn btn-danger dropdown-toggle" data-toggle="dropdown">
				Pins
			</button>
			<div class="dropdown-menu">
				%s
			</div>
        </div>    
    </div>
    
    <h4 style="color:bisque">Table of pins set and used on the board</h4>
    <main class="d-flex m-auto" style="width: 720px; margin-top:10px !important;" >
        <table class="table table-dark">
            <tr class="table-dark"><th>Pin</th><th>Value</th></tr>
            %s
        </table>
    </main>
    <h4 style="color:bisque">Table of sensors set and used on the board</h4>
    <main class="d-flex m-auto" style="width: 720px; margin-top:10px !important;" >
        <table class="table table-dark">
            <tr class="table-dark"><th>Sensor</th><th>Input</th></tr>
            %s
        </table>
    </main>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
</body>
</html>
"""


# On-board code

#To test ADC connect the potentiometer in pin number 33

# Initialize I2C temperature sensor
temp_addr = 24
temp_reg = 5
res_reg = 8

Pin(15,Pin.OUT).value(0)

# Function for obtaining temperature from bytearray
def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp
# Call temp_c(data) for computed temperature

# Select pins
pinset = (0, 2, 4, 5, 12, 14, 15, 21, 22, 23, 32, 33)
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
        # GET Request is found
        if line.find(b'GET') != -1:
            # Transform to string, go in between GET and HTTP
            # strip() used to remove whitespaces in the path
            respath = str(line).split('GET')[1].split('HTTP')[0].strip()
            pathlist = respath.split('/')
            #Set status code
            client.send("HTTP/1.1 200 OK\n")
            if pathlist[1] == '':
                #Create response
                droppins = ['<a class="dropdown-item" href="http://192.168.4.1:80/pins/pin%s">Pin %s</a>' %
                            (str(pno),str(pno)) for pno in pinset]
                
                rows = ['<tr %s><td>%s</td><td>%d</td></tr>' %
                        ('class="table-success"' if p.value() else 'class="table-danger"',
                         str(p), p.value()) for p in pins]
                
                sensrows = []
                try:
                    i2c = I2C(scl=Pin(22), sda=Pin(23))
                    data = bytearray(2)
                    i2c.readfrom_mem_into(temp_addr, temp_reg, data)
                    sensrows.append('<tr class="table-warning"><td>%s</td><td>%d °C</td></tr>' %
                            ("Temperature",temp_c(data)))
                except:
                    pass
                try:
                    #Initialize Analog-Digital Converter 
                    adc = ADC(Pin(33))
                    adc.width(ADC.WIDTH_12BIT)
                    adc.atten(ADC.ATTN_11DB)
                    sensrows.append('<tr class="table-warning"><td>%s</td><td>%d</td></tr>' %
                            ("Analog-Digital Converter (Potentiometer)",adc.read()))
                except:
                    pass
                try:
                    #Initialize button
                    button = Pin(14, Pin.IN, Pin.PULL_UP)
                    sensrows.append('<tr class="table-warning"><td>%s</td><td>%d</td></tr>' %
                            ("Button Press",1-button.value()))
                except:
                    pass
                response = html % ('\n'.join(droppins),'\n'.join(rows),'\n'.join(sensrows))
                client.send("Content-Type: text/html\n")

            elif (pathlist[1] == 'sensors'):
                if len(pathlist) == 2:
                    #List of sensors
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
                        button = Pin(14, Pin.IN, Pin.PULL_UP)
                        response = json.dumps(
                            {"name": "button", "value": button.value()})
                    except:
                        response = json.dumps(
                            {"error": "Button not connected."})
                        
                elif pathlist[2] == 'potentiometer':
                    try:
                        #Initialize Analog-Digital Converter 
                        adc = ADC(Pin(32))
                        adc.width(ADC.WIDTH_12BIT)
                        adc.atten(ADC.ATTN_11DB)
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
                    #List of pins
                    response = json.dumps(pinlist)
                else:
                    try:
                        no = int(pathlist[2].split('pin')[-1])
                        pinname = "Pin {}".format(no)
                        val = pins[pinset.index(no)].value()
                        response = json.dumps(
                            {"name": pinname, "value": val})
                    except:
                        response = json.dumps(
                            {"error": "No such pin exists."})

            if len(pathlist[1]) > 1:
                client.send("Content-Type: application/json\n")
        # POST Request is found
        # elif line.find(b'POST')!=-1:
        # DELETE Request is found
        # elif line.find(b'DELETE')!=-1:
        elif line.find(b'POST') != -1:
            # Transform to string, go in between PATCH and HTTP
            # strip() used to remove whitespaces in the path
            respath = str(line).split('POST')[1].split('HTTP')[0].strip()
            if respath.find('?p') != -1:    
                try:    
                    #Parse for led pin number and value to be set
                    pair = respath.split('?p')[1].split('=')
                    pinno = int(pair[0])
                    pinval = int(pair[1])
                    led = Pin(pinno,Pin.OUT)
                    led.value(0)
                    #Set new value of led (toggle)
                    led.value(pinval)
                    print("LED Toggled")
                    #Set status code
                    client.send("HTTP/1.1 200 OK\n")
                    #Send response that the LED is toggled
                    response = json.dumps({"success":"LED is toggled successfully."})
                except:
                    client.send("HTTP/1.1 503 Service Unavailable")
                    response = json.dumps({
                        "error":"LED cannot be toggled on/off."})
            
            elif respath.find('?neo') != -1:
                try:
                    #Parse for new RGB combination    
                    color = respath.split('?neo')[1].split('=')[1].split('-')
                    vred = int(color[0])
                    vgreen = int(color[1])
                    vblue = int(color[2])
                    neo = neopixel.NeoPixel(Pin(4,Pin.OUT),2)
                    #Set order to RGB
                    neo.ORDER = (0,1,2)
                    #Set the new color on neoPixels
                    neo[0] = (vred,vgreen,vblue)
                    neo[1] = (vred,vgreen,vblue)
                    neo.write()
                    neo.write()
                    print("NeoPixel Changed Color")
                    #Set status code
                    client.send("HTTP/1.1 200 OK\n")
                    response = json.dumps({"success":"NeoPixel LED is updated successfully."})
                except:
                    client.send("HTTP/1.1 503 Service Unavailable")
                    response = json.dumps({
                        "error":"NeoPixel LED cannot be updated."})
                
        if not line or line == b'\r\n':
            break
    client.send("\n"+response)
    client.close()
