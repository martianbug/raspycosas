from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher

global humidity
global temp

def get_data(address, *args):
    # global temp
    # global humidity
    # temp = args[0]
    # humidity = args[2]
    try:
        # print(temp)
        print(f"{address}: {args}")
    except ValueError: pass

if __name__ == "__main__":
    # Parse command line arguments
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--ip", default="127.0.0.1", help="The ip to listen on")
    # parser.add_argument("--port", type=int, default=5005, help="The port to listen on")
    # args = parser.parse_args()
    ip ="192.168.1.18"
    port = 5005
    port = 9999
    dispatcher = Dispatcher()
    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatcher)
    
    dispatcher.map("/data", get_data)
    # server.dispatcher.map("/test", print_handler)
    
    print(f"Serving on {server.server_address}")
    # msg = server.get_request()
    server.serve_forever()
    