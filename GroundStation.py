from inputs import get_gamepad
import math
import threading
import struct
import serial
import time
import sys


class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)
    WINDOW_SIZE = 3  # Adjust the window size for more or less smoothing

    def __init__(self):
        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self.target_LeftJoystickY = 0
        self.target_LeftJoystickX = 0
        self.target_RightJoystickY = 0
        self.target_RightJoystickX = 0

        self.LeftJoystickY_history = []
        self.RightJoystickX_history = []

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        self.uart_packet = None

    def read(self):
        self.target_LeftJoystickY = self.LeftJoystickY
        self.target_RightJoystickX = self.RightJoystickX
        a = self.A
        b = self.X
        rb = self.RightBumper

        self._smooth_speeds()

        device_id = 1
        start_bit = 1 << 7

        self.uart_packet = struct.pack('@BBbb', start_bit | device_id, 0b00000011, int(self.LeftJoystickY / 2), int(self.RightJoystickX / 2))

    def write_uart(self):
        print(self.uart_packet)
        ser.write(self.uart_packet)

    def _smooth_speeds(self):
        self.LeftJoystickY = self._smooth_value(self.LeftJoystickY_history, self.target_LeftJoystickY)
        self.RightJoystickX = self._smooth_value(self.RightJoystickX_history, self.target_RightJoystickX)

    def _smooth_value(self, history, new_value):
        history.append(new_value)
        if len(history) > XboxController.WINDOW_SIZE:
            history.pop(0)
        return sum(history) / len(history)

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    self.LeftJoystickY = int(event.state / XboxController.MAX_JOY_VAL * 100)
                    if abs(self.LeftJoystickY) <= 20:
                        self.LeftJoystickY = 0
                elif event.code == 'ABS_X':
                    self.LeftJoystickX = int(event.state / XboxController.MAX_JOY_VAL * 100)
                    if abs(self.LeftJoystickX) <= 20:
                        self.LeftJoystickX = 0
                elif event.code == 'ABS_RY':
                    self.RightJoystickY = int(event.state / XboxController.MAX_JOY_VAL * 100)
                    if abs(self.RightJoystickY) <= 20:
                        self.RightJoystickY = 0
                elif event.code == 'ABS_RX':
                    self.RightJoystickX = int(event.state / XboxController.MAX_JOY_VAL * 100)
                    if abs(self.RightJoystickX) <= 20:
                        self.RightJoystickX = 0
                elif event.code == 'ABS_Z':
                    self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'ABS_RZ':
                    self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL
                elif event.code == 'BTN_TL':
                    self.LeftBumper = event.state
                elif event.code == 'BTN_TR':
                    self.RightBumper = event.state
                elif event.code == 'BTN_SOUTH':
                    self.A = event.state
                elif event.code == 'BTN_NORTH':
                    self.Y = event.state
                elif event.code == 'BTN_WEST':
                    self.X = event.state
                elif event.code == 'BTN_EAST':
                    self.B = event.state
                elif event.code == 'BTN_THUMBL':
                    self.LeftThumb = event.state
                elif event.code == 'BTN_THUMBR':
                    self.RightThumb = event.state
                elif event.code == 'BTN_SELECT':
                    self.Back = event.state
                elif event.code == 'BTN_START':
                    self.Start = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY1':
                    self.LeftDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY2':
                    self.RightDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY3':
                    self.UpDPad = event.state
                elif event.code == 'BTN_TRIGGER_HAPPY4':
                    self.DownDPad = event.state


def handshake():
    while(True):
        ser.write(struct.pack('@B', 0x01))
        ack_data = ser.read(1)
        # print(ack_data)
        if ack_data == b'\x81':
            break
    print("Handshake Complete")
    
    


if __name__ == '__main__':
    #TODO: implment handshake logic
    #TODO: implement dynamic output (only when value change)
    #TODO: setup on UWRT computer
    ser = serial.Serial('/dev/ttyUSB0', 57600)  # open serial port
    joy = XboxController()
    handshake()
    while True:
        joy.read()
        joy.write_uart()
        print(struct.unpack("@bb", ser.read(2)))
        