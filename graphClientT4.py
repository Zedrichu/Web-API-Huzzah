import requests
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#Select time period of the entire plotting 
t = int(input("Enter the period of time in seconds: "))
#Select time interval between two recordings
period = int(input("Enter the time for each measurement (secs): "))
file = open('data.txt', 'w')
now = 0


x_vals = []
y_vals = []


def animate(i):
    if i > t:
        #After the time set by user the animation terminates
        anim.event_source.stop()
        plt.savefig('data.png')

    #Obtain the temperature from the API
    response = requests.get('http://192.168.4.1/sensors/temperature')
    temp = response.json()['value']
    print("Temperature recorded: {}".format(temp))
    #Perform the real-time plotting
    x_vals.append(i)
    y_vals.append(temp)
    plt.cla()
    plt.plot(x_vals, y_vals)
    plt.xlabel('Recordings (interval %d sec)' % period)
    plt.ylabel('Temperature')
    plt.title('Temperature sensor data over time')
    #Save the date recorded in a .txt file
    with open('data.txt', 'a') as file:
        file.write("{},{}\n".format(temp, time.time()))

#Animate plot
anim = FuncAnimation(plt.gcf(), animate, interval=period*1000)
plt.tight_layout()
plt.show()
