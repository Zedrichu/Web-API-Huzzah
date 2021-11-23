import machine
import socket


pins = [machine.Pin(i, machine.Pin.IN) for i in (0, 2, 4, 5, 12, 13, 14, 15)]

html = """<!DOCTYPE html>
<html>
    <head> <title>ESP32 Pins</title> </head>
    <body> <h1>ESP32 Pins</h1>
        <table border="1"> <tr><th>Pin</th><th>Value</th></tr> %s </table>
    </body>
</html>
"""

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

# stuff on board
button = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(23))
address = 24
temp_reg = 5
res_reg = 8


def temp_c(data):
    value = data[0] << 8 | data[1]
    temp = (value & 0xFFF) / 16.0
    if value & 0x1000:
        temp -= 256.0
    return temp


print('listening on', addr)

while True:
    cl, addr = s.accept()
    print('client connected from', addr)
    cl_file = cl.makefile('rwb', 0)
    while True:
        line = cl_file.readline()
        if not line or line == b'\r\n':
            break
    rows = ['<tr><td>%s</td><td>%d</td></tr>' %
            (str(p), p.value()) for p in pins]
    data = bytearray(2)
    i2c.readfrom_mem_into(address, temp_reg, data)
    rows.append('<tr><td>%s</td><td>%d</td></tr>' %
                ("Temperature", temp_c(data)))
    rows.append('<tr><td>%s</td><td>%d</td></tr>' %
                ("Button press", button.value()))
    response = html % '\n'.join(rows)
    cl.send(response)
    cl.close()
c
