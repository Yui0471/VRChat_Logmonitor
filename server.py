# -*- coding : utf-8 -*-

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

demo = """
######################################
#                                    #
#   VRChat Log Monitor               #
#           OSC Server v 0.0.0       #
#                                    #
######################################

[info] VRChatからのOSCを受信します
[Warning!] 本スクリプトを使用するにはSteam版VRChatが必要です

[info] 開始するにはEnterを押してください
"""

input(demo)
print("[info] OSC通信の監視を開始します")

def print_handler(address, *args):
    print(f"{address}: {args}")

def default_handler(address, *args):
    print(f"DEFAULT {address}: {args}")

dispatcher = Dispatcher()
dispatcher.map("*", print_handler)
dispatcher.set_default_handler(default_handler)

ip = "127.0.0.1"
port = 9001

server = BlockingOSCUDPServer((ip, port), dispatcher)
server.serve_forever()