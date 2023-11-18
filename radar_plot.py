import serial
import sys
import glob
import matplotlib.pyplot as plt
import numpy as np

# Constants
THETA_MIN = 0
THETA_MAX = 180
BAUD_RATE = 500000

# Function to search for available serial ports
def port_search():
    # Determine available serial ports based on the operating system
    if sys.platform.startswith('win'):  # Windows
        ports = ['COM{0:1.0f}'.format(ii) for ii in range(1, 256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')  # Linux or Cygwin
    elif sys.platform.startswith('darwin'):  # MAC
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Machine Not pyserial Compatible')

    arduinos = []
    for port in ports:
        if len(port.split('Bluetooth')) > 1:
            continue
        try:
            ser = serial.Serial(port)
            ser.close()
            arduinos.append(port)  # If we can open it, consider it an Arduino
        except (OSError, serial.SerialException):
            pass
    return arduinos

# Function to open a serial port
def open_serial_port(port, baud_rate):
    try:
        ser = serial.Serial(port, baud_rate)
    except serial.SerialException as e:
        print(f"Could not open port {port}: {e}")
        sys.exit(1)
    return ser

# Function to read data from the serial port and plot it
def read_and_plot_data(ser, ax):
    while True:
        try:
            line = ser.readline()
            line_str = line.decode().rstrip('\n')
            line_str = line_str.replace("b'", "").replace("'", "")
            parts = line_str.split(',')
            if parts[0].replace('.', '').isdigit():
                angle_degrees = int(parts[0])
                distance = float(parts[1])
                plot_data(ax, angle_degrees, distance)
        except Exception as e:
            print(f"An error occurred: {e}")

# Function to plot data on a polar plot
def plot_data(ax, angle_degrees, distance):
    ax.clear()
    angle_rad = np.radians(angle_degrees)
    ax.plot([0, angle_rad], [0, distance], color="red")
    ax.text(0.95, 0.95, f'Angle: {angle_degrees}°, Distance: {distance}cm', color="black", transform=ax.transAxes,
            horizontalalignment='right', verticalalignment='top')
    ax.set_thetamin(THETA_MIN)
    ax.set_thetamax(THETA_MAX)
    limit = (distance // 20) + 1
    plt.ylim(0, limit * 20)
    plt.pause(0.01)

# Main function
def main():
    port = port_search()[0]  # Get the first available port
    ser = open_serial_port(port, BAUD_RATE)  # Open the serial port
    ser.flush() # clear the port
    ax = plt.subplot(111, projection='polar')  # Create a polar plot
    plt.subplots_adjust(top=1.0, bottom=0.0, left=0.125, right=0.9, hspace=0.2, wspace=0.2)
    ax.set_facecolor('black')
    plt.grid(color='green')
    read_and_plot_data(ser, ax)  # Read and plot data from the serial port

if __name__ == "__main__":
    main()

