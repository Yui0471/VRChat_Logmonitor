# -*- coding : utf-8 -*-

import time
from pythonosc.udp_client import SimpleUDPClient

demo = """
######################################
#                                    #
#   VRChat Log Monitor               #
#          demo script v 0.0.0       #
#                                    #
######################################

[info] アバターにセットアップされたオブジェクトをテストします
[info] 全ての桁を0から9まで表示テストできます
[Warning!] 本スクリプトを使用するにはSteam版VRChatが必要です

[info] 開始するにはEnterを押してください
"""

input(demo)

ip = "127.0.0.1"
port = 9000
client = SimpleUDPClient(ip, port)

parameter = 1

while parameter != 81:
    print(parameter)
    client.send_message("/avatar/parameters/Log_Monitor", parameter)
    time.sleep(0.5)
    parameter += 1

client.send_message("/avatar/parameters/Log_Monitor", 0)

print("[info] 送信テストを完了しました")
input("[info] Enterを押して終了してください")