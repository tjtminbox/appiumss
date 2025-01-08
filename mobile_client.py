from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
import base64
import json
import logging
import socketio
import platform
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MobileScreenshotClient:
    def __init__(self, server_url, device_name=None, udid=None):
        self.server_url = server_url
        self.device_name = device_name
        self.udid = udid
        self.driver = None
        self.sio = socketio.Client()
        self.platform = None
        self.setup_socket_events()

    def setup_socket_events(self):
        @self.sio.event
        def connect():
            logger.info("Connected to server")

        @self.sio.event
        def disconnect():
            logger.info("Disconnected from server")
            self.stop()

        @self.sio.event
        def error(error):
            logger.error(f"Socket error: {error}")
            self.stop()

    def setup_driver(self):
        try:
            # Detect platform and set capabilities
            if platform.system() == 'Darwin':  # macOS - assume iOS
                self.platform = 'iOS'
                caps = {
                    'platformName': 'iOS',
                    'automationName': 'XCUITest',
                    'deviceName': self.device_name or 'iPhone',
                    'udid': self.udid,
                    'noReset': True
                }
            else:  # Assume Android
                self.platform = 'Android'
                caps = {
                    'platformName': 'Android',
                    'automationName': 'UiAutomator2',
                    'deviceName': self.device_name or 'Android Device',
                    'noReset': True
                }

            if self.udid:
                caps['udid'] = self.udid

            # Connect to Appium server
            self.driver = webdriver.Remote('http://localhost:4723/wd/hub', caps)
            logger.info(f"Connected to {self.platform} device")
            return True

        except Exception as e:
            logger.error(f"Failed to setup driver: {e}")
            return False

    def take_screenshot(self):
        try:
            # Take screenshot
            screenshot = self.driver.get_screenshot_as_base64()
            
            # Prepare device info
            device_info = {
                'platform': self.platform,
                'device_name': self.device_name or 'unknown',
                'udid': self.udid or 'unknown'
            }
            
            # Send to server
            self.sio.emit('screenshot', {
                'image': f'data:image/png;base64,{screenshot}',
                'device_info': device_info,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.info("Screenshot taken and sent to server")
            return True

        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    def start(self):
        try:
            # Connect to socket server
            self.sio.connect(self.server_url)
            
            # Setup Appium driver
            if not self.setup_driver():
                raise Exception("Failed to setup driver")

            logger.info("Screenshot client started successfully")
            
            # Take initial screenshot
            self.take_screenshot()
            
        except Exception as e:
            logger.error(f"Error starting client: {e}")
            self.stop()

    def stop(self):
        try:
            if self.driver:
                self.driver.quit()
            if self.sio.connected:
                self.sio.disconnect()
        except Exception as e:
            logger.error(f"Error stopping client: {e}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mobile Screenshot Client")
    parser.add_argument("server_url", help="Screenshot server URL (e.g., http://localhost:5000)")
    parser.add_argument("--device-name", help="Device name (optional)")
    parser.add_argument("--udid", help="Device UDID (optional)")
    
    args = parser.parse_args()
    
    client = MobileScreenshotClient(
        server_url=args.server_url,
        device_name=args.device_name,
        udid=args.udid
    )
    
    try:
        client.start()
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping client...")
        client.stop()

if __name__ == "__main__":
    main()
