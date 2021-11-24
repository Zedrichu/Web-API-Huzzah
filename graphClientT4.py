import requests
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


t = int(input("Enter the period of time in seconds: "))
period = int(input("Enter the time for each measurement (secs): "))
file = open('data.txt', 'w')
now = 0


x_vals = []
y_vals = []


def animate(i):
    if i > t:
        anim.event_source.stop()
        plt.savefig('data.png')

    response = requests.get('http://192.168.4.1/sensors/temperature')
    temp = response.json()['value']
    print("Temperature recorded: {}".format(temp))
    x_vals.append(i)
    y_vals.append(temp)
    plt.cla()
    plt.plot(x_vals, y_vals)
    plt.xlabel('Time passed (secs)')
    plt.ylabel('Temperature')
    plt.title('Temperature sensor data over time')
    with open('data.txt', 'a') as file:
        file.write("{},{}\n".format(temp, time.time()))


anim = FuncAnimation(plt.gcf(), animate, interval=period*1000)
plt.tight_layout()
plt.show()
