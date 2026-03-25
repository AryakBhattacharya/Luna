import os
import ctypes


class SystemControl:

    # ------------------------------
    # VOLUME
    # ------------------------------
    @staticmethod
    def volume_up():
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
        return "Volume increased."

    @staticmethod
    def volume_down():
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
        return "Volume decreased."

    @staticmethod
    def volume_mute():
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
        return "Volume toggled."


    # ------------------------------
    # WIFI (toggle)
    # ------------------------------
    @staticmethod
    def wifi_settings():
        os.system('start ms-settings:network-wifi')
        return "I’ve opened Wifi controls for you"

    @staticmethod
    def wifi_on():
        result = os.system('netsh interface set interface "Wi-Fi" enabled')
        if result != 0:
            return "I need administrator permission to control WiFi."
        return "WiFi turned on."

    @staticmethod
    def wifi_off():
        result = os.system('netsh interface set interface "Wi-Fi" disabled')
        if result != 0:
            return "I need administrator permission to control WiFi."
        return "WiFi turned off."


    # ------------------------------
    # BLUETOOTH (opens toggle panel fallback)
    # ------------------------------
    @staticmethod
    def bluetooth_settings():
        os.system('start ms-settings:bluetooth')
        return "I’ve opened Bluetooth controls for you"
    
    @staticmethod
    def bluetooth_on():
        os.system('start ms-settings:bluetooth')
        return "I’ve opened Bluetooth controls for you"

    @staticmethod
    def bluetooth_off():
        os.system('start ms-settings:bluetooth')
        return "I’ve opened Bluetooth controls for you"


    # ------------------------------
    # AIRPLANE MODE (fallback)
    # ------------------------------
    @staticmethod
    def airplane_mode():
        os.system('start ms-settings:network-airplanemode')
        return "I’ve opened Airplane controls for you"
    
    @staticmethod
    def airplane_on():
        os.system('start ms-settings:network-airplanemode')
        return "I’ve opened Airplane controls for you"
        
    @staticmethod
    def airplane_off():
        os.system('start ms-settings:network-airplanemode')
        return "I’ve opened Airplane controls for you"