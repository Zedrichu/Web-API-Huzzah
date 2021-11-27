
import json
import requests
from requests.api import head

items = ['Get value of a specific pin.', 'Toggle red LED.', 'Toggle orange LED.',
         'Toggle green LED.', 'Change NEOPIXEL color.', 'Quit.']


def menu():
    for i in range(len(items)):
        print('{}. {}'.format(i+1, items[i]))

    try:
        return int(input("Choose an option from above. "))
    except:
        print("Not a valid option. Try again.")
        menu()


while True:
    choice = menu()
    if choice == 1:
        chosen_pin = int(input("Pin no: "))

        request = requests.get(
            'http://192.168.4.1/pins/pin{}'.format(chosen_pin)).json()
        try:
            print(request['error'])
        except:
            print('Value: {}.'.format(request['value']))

    elif choice == 2:
        #RED Led in pin 15
        request = requests.get(
            'http://192.168.4.1/pins/pin15').json()
        try:
            print(request['error'])
        except:
            pass
        val = '?p15='+str(1-request['value'])
        header = {'Content-Type':'application/json'}
        request = requests.post(
            'http://192.168.4.1/post'+val,headers=header)
        print(request.status_code)
        request = request.json()
        try:
            print(request['error'])
        except:
            print('Red '+request['success'])
        
    elif choice == 3:
        #ORANGE Led in pin 32
        request = requests.get(
            'http://192.168.4.1/pins/pin32').json()
        try:
            print(request['error'])
        except:
            pass
        val = '?p32='+str(1-request['value'])
        header = {'Content-Type':'application/json'}
        request = requests.post(
            'http://192.168.4.1/post'+val,headers=header)
        print(request.status_code)
        request = request.json()
        try:
            print(request['error'])
        except:
            print('Orange '+request['success'])
            
    elif choice == 4:    
        #GREEN Led in pin 21
        request = requests.get(
            'http://192.168.4.1/pins/pin21').json()
        try:
            print(request['error'])
        except:
            pass
        val = '?p21='+str(1-request['value'])
        header = {'Content-Type':'application/json'}
        request = requests.post(
            'http://192.168.4.1/post'+val,headers=header)
        print(request.status_code)
        request = request.json()
        try:
            print(request['error'])
        except:
            print('Green '+request['success'])
    
    elif choice == 5:
        #NEOPIXEL Led in pin 4
        try:
            vred = int(input("Type red led value (0-255): "))
            vgreen = int(input("Type green led value (0-255): "))
            vblue = int(input("Type blue led value (0-255): "))
        except:
            pass
        val = '?neo=%d-%d-%d' % (vred,vgreen,vblue)
        header = {'Content-Type':'application/json'}
        request = requests.post(
            'http://192.168.4.1/post'+val,headers=header)
        print(request.status_code)
        request = request.json()
        try:
            print(request['error'])
        except:
            print(request['success'])
        
    else:
        break
        
