import socket
import threading
import time
import pyautogui
import json
import queue

data_queue = queue.Queue()

udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

class Cprint:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    RESET = "\033[0m"

    @classmethod
    def red(cls, statement):
        print(f"{cls.RED}{statement}{cls.RESET}")
    

    @classmethod
    def green(cls, statement):
        print(f"{cls.GREEN}{statement}{cls.RESET}")
    

    @classmethod
    def blue(cls, statement):
        print(f"{cls.BLUE}{statement}{cls.RESET}")
    


class Events :

    width_ratio  = 0.0
    height_ratio = 0.0

    @classmethod    
    def on_pan_update(cls,data):
        
        x = (data["x"] * cls.width_ratio) * 1.5
        y = (data["y"] * cls.height_ratio) *1.5
        
        # print(f"x : {x} and y : {y}")
        pyautogui.moveRel(x, y)


    @classmethod    
    def on_tap_down(cls):
        pyautogui.click()

    @classmethod    
    def on_double_tap_down(cls):
        pyautogui.doubleClick()

    @classmethod    
    def on_right_click(cls):
        pyautogui.rightClick()

    @classmethod    
    def on_keyboard(cls, data):
        pyautogui.write(data["data"]);

    @classmethod    
    def set_ratio(cls,data):
        width, height = pyautogui.size()
        cls.width_ratio = width/data["x"]
        cls.height_ratio = height / data["y"]

        print(f"W : {cls.width_ratio} H : {cls.height_ratio}")


def udp_broadcast():
    global udp_server
    UDP_PORT = 36578

    # Create a udp server.
    # Provider configration to udp socket like allow broadcasting to all networks by 1.
    udp_server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


    while True:
        message = f"SERVER_HERE".encode()
        udp_server.sendto(message, ("<broadcast>", UDP_PORT))
        time.sleep(2)

def worker_loop():
    while True :

        
        decodedData =  data_queue.get()
        if not decodedData:
            continue;
        
        match decodedData["event"]:
            case "dimenstions":
                Events.set_ratio(decodedData)
            case "on_tap_down":
                Events.on_tap_down()
            case "on_double_tap_down":
                Events.on_double_tap_down()
            case "on_right_click":
                Events.on_right_click()
            case "on_pan_update":
                Events.on_pan_update(decodedData)
            case "on_keyboard":
                Events.on_keyboard(decodedData)
            case _:
                print("No Event Found:", decodedData)



def start_vx_connect():
    """Start Your Vx Connect Application Server ;)"""
    global udp_server

    HOST = "0.0.0.0"
    PORT = 8087

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        Cprint.green(f"Listening on {HOST}:{PORT}")

        client, addr = server_socket.accept()

        Cprint.blue(f"{addr} is connected with server,\nDo you want to continue connection (y/N) :")
        
        ans = input().lower().strip()

        if ans != "y" and ans != "yes":
            Cprint.red("Socket Connection Closed :)")
            server_socket.close()
            return
        
        buffer = ""
        while True:

            data = client.recv(1024).decode("utf-8")

            if not data:
                continue

            buffer += data

            while "^" in buffer:

                line, buffer = buffer.split("^", 1)
                print(line)

                try:
                    decodedData = json.loads(line)
                    data_queue.put(decodedData)

                except Exception as e:
                            print(f"Error: {e}")
                            udp_server.close()
                            server_socket.close();
                            break;

                    

    except Exception as e:
        server_socket.close();
        udp_server.close()
        Cprint.red(f"Server error: {e}")

    


if __name__ == "__main__":
    # threading.Thread(target=start_vx_connect, daemon=True).start()
    threading.Thread(target=udp_broadcast, daemon=True).start()
    threading.Thread(target=worker_loop, daemon=True).start()
    start_vx_connect()
        


