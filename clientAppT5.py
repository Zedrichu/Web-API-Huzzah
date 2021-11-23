import requests

items = ['Get value of a specific pin.', 'Turn on/off red LED.', 'Turn on/off orange LED.',
         'Turn on/off green LED.', 'Turn on/off NEOPIXELS.', 'Change NEOPIXELS color.', 'Quit.']


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

        res = requests.get(
            'http://192.168.4.1/pins/pin{}'.format(chosen_pin)).json()
        try:
            print(res['error'])
        except:
            print('Value: {}.'.format(res['value']))

    else:
        break
