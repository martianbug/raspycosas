from pythonosc import osc_server
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from bot_constants import *
def set_filter(address: str, *args) -> None:
    # We expect two float arguments
    if not len(args) == 2 or type(args[0]) is not float or type(args[1]) is not float:
        return
    # Check that address starts with filter
    if not address[:-1] == "/filter":  # Cut off the last character
        return

    value1 = args[0]
    value2 = args[1]
    filterno = address[-1]
    print(f"Setting filter {filterno} values: {value1}, {value2}")

def print_handler(address, *args):
    print(f"{address}: {args}")


def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")


dispatcher = Dispatcher()
dispatcher.map("/test*", print_handler)
dispatcher.set_default_handler(default_handler)


server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()  # Blocks forever

pass