#   A class for managing DELUX M800 ULTRA Mouse communication.
#   Author: @scandnk52

import usb.core
import usb.util

class Device:

    # Attributes:
    #    vid (int): Vendor ID of the device.
    #    pid (int): Product ID of the device.
    #    interface (int): Interface number to communicate with the device.
    def __init__(self, vid, pid, wired_pid, interface):
        self.__vid = vid
        self.__pid = pid
        self.__wired_pid = wired_pid
        self.__interface = interface
        self.__device = self.__get_device()

    # Find the USB device using VID and PID.
    def __get_device(self):
        device = usb.core.find(idVendor=self.__vid, idProduct=self.__pid)
        wired_device = usb.core.find(idVendor=self.__vid, idProduct=self.__wired_pid)

        if device is None and wired_device is None:
            raise ValueError(f"No such device found or connected!")
        return device or wired_device

    # Connect to the device by detaching kernel driver (if needed),
    # Claiming the interface, and setting an alternate interface setting.
    def __connect_device(self):
        try:
            if self.__device.is_kernel_driver_active(self.__interface):
                self.__device.detach_kernel_driver(self.__interface)

            usb.util.claim_interface(self.__device, self.__interface)
            self.__device.set_interface_altsetting(interface=self.__interface, alternate_setting=0)
        except usb.core.USBError as e:
            raise ValueError(f"Error connecting to device: {e}")

    # Release the interface and reattach the kernel driver.
    def __disconnect_device(self):
        try:
            usb.util.release_interface(self.__device, self.__interface)
            self.__device.attach_kernel_driver(self.__interface)
        except usb.core.USBError as e:
            raise ValueError(f"Error disconnecting from device: {e}")

    # Send data to the device using a control transfer.
    def __write_data(self, data):
        try:
            request = self.__device.ctrl_transfer(
                bmRequestType=0x21,
                bRequest=0x09,
                wValue=0x0204,
                wIndex=0x0001,
                data_or_wLength=data,
                timeout=1000
            )
        except usb.core.USBError as e:
            raise ValueError(f"Error writing data: {e}")
        return request

    # Read data from the device using a control transfer.
    def __read_data(self):
        try:
            response = self.__device.ctrl_transfer(
                bmRequestType=0xa1,
                bRequest=0x01,
                wValue=0x0204,
                wIndex=0x0001,
                data_or_wLength=64,
                timeout=1000
            )
        except usb.core.USBError as e:
            raise ValueError(f"Error reading data: {e}")
        return response

    # Public method to send data to the device.
    def send_data(self, data):
        self.__connect_device()
        self.__write_data(data)
        self.__disconnect_device()

    # Public method to send data to the device and receive a response.
    def get_data(self, data):
        self.__connect_device()
        self.__write_data(data)
        request = self.__read_data()
        self.__disconnect_device()

        return request