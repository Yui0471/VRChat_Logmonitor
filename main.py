# -*- coding:utf-8 -*-

import os
import sys
import time
import glob
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer
import asyncio
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
import ipaddress

moni = """
######################################
#                                    #
#   VRChat Log Monitor               #
#                  Version 4.2.0     #
#                                    #
######################################

[info] 現在のワールド、インスタンス人数をログから取得します
[Warning!] 本スクリプトを使用するにはSteam版VRChatが必要です
"""

#   Author : Yui-Kazeniwa
#   Support : Rounz
#   Original plan : dk_vrc_ff

# OSC用IPとPORTをセット
ip = "127.0.0.1"
send_port = 9000
receive_port = 9001

# パラメータ用辞書の定義
param_dict_first = {
    0:1,
    1:2,
    2:3,
    3:4,
    4:5,
    5:6,
    6:7,
    7:8,
    8:9,
    9:10
}

param_dict_second = {
    0:11,
    1:12,
    2:13,
    3:14,
    4:15,
    5:16,
    6:17,
    7:18,
    8:19,
    9:20
}

param_dict_third = {
    0:21,
    1:22,
    2:23,
    3:24,
    4:25,
    5:26,
    6:27,
    7:28,
    8:29,
    9:30
}

param_dict_fourth = {
    0:31,
    1:32,
    2:33,
    3:34,
    4:35,
    5:36,
    6:37,
    7:38,
    8:39,
    9:40
}

param_dict_fifth = {
    0:41,
    1:42,
    2:43,
    3:44,
    4:45,
    5:46,
    6:47,
    7:48,
    8:49,
    9:50
}

param_dict_sixth = {
    0:51,
    1:52,
    2:53,
    3:54,
    4:55,
    5:56,
    6:57,
    7:58,
    8:59,
    9:60
}

param_dict_seventh = {
    0:61,
    1:62,
    2:63,
    3:64,
    4:65,
    5:66,
    6:67,
    7:68,
    8:69,
    9:70
}

param_dict_eighth = {
    0:71,
    1:72,
    2:73,
    3:74,
    4:75,
    5:76,
    6:77,
    7:78,
    8:79,
    9:80
}

# IPアドレスのチェック
def ip_check(ip):
    try:
        ip_set = ipaddress.ip_address(ip)

        if type(ip_set) is ipaddress.IPv4Address:
            return str(ip_set)

        else:
            input("[Error!] 入力されたIPアドレスは使用できません")
            sys.exit()
        
    except ValueError:
        input("[Error!] IPアドレスに使用できない値が含まれています")
        sys.exit()


# ポートのチェック
def port_check(values):
    if values.isascii() and values.isdecimal(): # ascii文字及び数字だったらTrue
        port = int(values)
        if 1 <= port <= 65535:
            return port

    input("[Error!] 入力されたポート番号は使用できません")
    sys.exit()


# 最新のログファイルを取得
def logfile_detection(directory_path):
    files = glob.glob(directory_path + "\\*")

    logfiles = []
    for s in files: # ログファイルのみを抽出
        if "output_log_" in s:
            logfiles.append(s)
        else:
            pass

    if len(logfiles) == 0: # ログファイルが見つからないと0になる
        print("[Error!] ログファイルが見つかりませんでした。VRChatを起動してから実行してください")
        input()
        print("[info] EnterかウインドウのXボタンで終了してください")
        sys.exit()
    
    latest = max(logfiles, key=os.path.getctime) # 最新のログファイルのパスを取得

    print("[info]", os.path.basename(latest), "ファイルを開きました")

    return latest


# ログファイルのある場所まで移動
def directory_move():
    username = os.getlogin()
    directory_path = "C:\\Users\\" + username + "\\Appdata\\LocalLow\\VRChat\\VRChat"
    
    try:
        os.chdir(directory_path)
        print("\n[info] VRChatディレクトリに移動しました")
        return directory_path

    except FileNotFoundError:
        print("[Error!] VRChatディレクトリが見つかりませんでした")
        sys.exit()

    
# txtを読み込み専用で開きデータを行ごとにリスト化する
def txt_open(path):
    f = open(path, "r", encoding="utf-8")
    data = f.read().split("\n")

    txtdata = []
    for s in data:
        if not s: # 空の要素が紛れ込むため消す
            pass
        else:
            txtdata.append(s)

    f.close()
    return txtdata


# 現在のワールド名にjoinしたときの行番号を取得
def current_world(data):
    count = 0
    worldcount = 0
    for s in reversed(data):
        if "Entering Room:" in s:
            world = s # ついでにワールド名も取れる
            break
        count += 1 # 行番号をカウント

    worldcount = len(data) - count -1

    if worldcount == -1: # 起動したてでワールド情報がログに出力されていない場合
        return None

    worldname_num = world.find("Entering Room:") + 15
    worldname = world[worldname_num :]
    
    return worldcount, worldname

    # 2022.08.20 16:25:22 Log        -  [Behaviour] Entering world
    # ワールド移動
    # 2022.08.20 16:25:22 Log        -  [Behaviour] Entering Room: Vket2022S Gate of Metaverse
    # joinするワールド名

# 現在同じインスタンスに居るプレイヤーを整理してリストに保存
def player_count(data, world_count): # list, int, list
    player = []
    del data[: world_count]

    for s in data: # ユーザ名だけ使うのでそれ以外は切り捨てる
        if "OnPlayerJoined " in s:
            playername_num = s.find("OnPlayerJoined ") + 15
            playername = s[playername_num :]
            player.append(playername)
        
        if "OnPlayerLeft " in s:
            playername_num = s.find("OnPlayerLeft ") + 13
            playername = s[playername_num :]
            player.remove(playername)

    return player

    # 2022.08.20 16:25:27 Log        -  [Behaviour] OnPlayerJoined [PlayerName]
    # プレイヤーがインスタンスにjoinする
    # 2022.08.20 16:28:02 Log        -  [Behaviour] OnPlayerLeft [PlayerName]
    # プレイヤーがインスタンスからLeftする

    # 既知のバグ
    # プレイヤー名に扱えない特殊文字があった場合リストにappendできずremove時にエラーが発生する


# 経過時間をhhmmssで返す
def elapsed_time_str(seconds):
    seconds = int(seconds + 0.5)
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds - h * 3600 - m * 60

    return f"{h:02}{m:02}{s:02}"


# OSC送信用のデータを全て取得しなおす
def refrash_send_data():
    global stay_time

    # 滞在時間計算部分
    now_time = int(time.time()) # 現在時刻
    # もし記録していたワールド名が現在のワールドと違っているか
    # インスタンス人数が0になったら書き換える
    if world_time_com[0] != world[1] or player_number == "00":
        world_time_com[0] = world[1]
        world_time_com[1] = now_time

    diff = now_time - world_time_com[1] # 差分
    stay_time = elapsed_time_str(diff) # インスタンス滞在時間hhmmss

    send_data = [ # 取得したデータを整理して格納
        param_dict_first[int(player_number[-2])],
        param_dict_second[int(player_number[-1])],
        param_dict_third[int(stay_time[-6])], 
        param_dict_fourth[int(stay_time[-5])],
        param_dict_fifth[int(stay_time[-4])],
        param_dict_sixth[int(stay_time[-3])],
        param_dict_seventh[int(stay_time[-2])],
        param_dict_eighth[int(stay_time[-1])]
    ]

    return send_data


# VRChatからのOSCを受信
def filter_handler(address, *args):
    #print("\n", f"{address}: {args}")

    # OSCでアバターが変更された場合"/avatar/change"が来ることで発火する
    if address == "/avatar/change":
        print("\n[info] アバターの変更を検知しました")
        print("[info] アバターのロード終了まで待っています……")
        time.sleep(5) # アバターロードが確実に終わるまで5秒待つ
        print("[info] データの更新を行っています……")

        send_data = refrash_send_data()

        for i in send_data:
            client.send_message("/avatar/parameters/Log_Monitor", i)
            time.sleep(0.5)

    # アバターがsit判定に座ることで発火する
    if address == "/avatar/parameters/InStation":
        print("\n[info] InStationを検知しました")
        time.sleep(1)
        print("[info] データの更新を行っています……")

        send_data = refrash_send_data()

        for i in send_data:
            client.send_message("/avatar/parameters/Log_Monitor", i)
            time.sleep(0.5)



# ログファイルを開いてリスト型に格納する処理
def fileload():
    global player_number
    global world
    global player_list

    logdata = txt_open(filepath)
    temp = current_world(logdata)

    if temp is None: # 取得できないとNoneが返る
        return

    world = temp
    player_list = player_count(logdata, world[0]) # プレイヤーのリストを取得
    player_number = str(len(player_list)).zfill(2) # プレイヤーの人数(有効数字二桁0埋め)


# ファイル変更を検知するHandler
class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        fileload()

    # ファイル変更を検知
    def on_modified(self, event):
        fileload()

    # ファイル作成を検知
    def on_created(self, event):
        global filepath

        if event.is_directory: # ディレクトリだったら無視
            return

        # output_log_ファイル以外だったら無視
        if "output_log_" not in os.path.basename(event.src_path):
            return

        if filepath == event.src_path: # 同じパスだったら無視
            return

        filepath = logfile_detection(directory_move()) # VRChatディレクトリを探してパスを返す


if __name__ == "__main__":
    print(moni)

    if [s for s in sys.argv if "--osc=" in s]:
        osc_argv = sys.argv[1]
        receive_port = port_check(osc_argv[6 : osc_argv.find(":")]) # 受信ポート
        ip = ip_check(osc_argv[osc_argv.find(":") +1 : osc_argv.rfind(":")]) # 送信先IP
        send_port = port_check(osc_argv[osc_argv.rfind(":") +1 :]) # 送信ポート

    print("[info] ログの監視を開始します")
    print("[info] 送信先IPアドレス :", ip, "送信ポート :", send_port, "受信ポート :", receive_port)
    print("[info] OSC送信を開始します")

    client = SimpleUDPClient(ip, send_port)

    filepath = logfile_detection(directory_move()) # VRChatディレクトリを探してパスを返す

    player_list = [] # プレイヤーリストの保存場所
    world_time_com = ["", 0] # 取得したワールド名と人数の保存場所
    OSC_send_data = [0] * 8 # 送信するOSCパラメータの保存場所
    send_data = [0] * 8 # OSCパラメータの最新情報
    player_number = "" # 現在のインスタンス人数
    world = [0, ""] # ワールドjoin時の行数, ワールド名
    player_list = [] # 同じインスタンスにいるプレイヤーのリスト
    stay_time = "" # ワールドjoin時からの経過時間

    dispatcher = Dispatcher()
    dispatcher.map("/avatar/*", filter_handler)

    async def main():
        global send_data
        global player_list
        global world_time_com
        global OSC_send_data
        global player_number
        global world
        global stay_time

        while True:

            #fileload()
            send_data = refrash_send_data()

            send_flag = False
            for i in range(8): # 前回と比較, 違う値があった場合OSCを送信
                if OSC_send_data[i] != send_data[i]:
                    if send_flag: # 前回送信していたら0.5秒待つ
                        await asyncio.sleep(0.5)
                    client.send_message("/avatar/parameters/Log_Monitor", send_data[i])
                    send_flag = True

            # OSCで送信したデータを保存
            for i in range(8):
                OSC_send_data[i] = send_data[i]

            # 表示崩れ防止のため15文字以上のワールド名は省略
            if len(world[1]) >= 15:
                worldname = world[1][:13] + "……"
            else:
                worldname = world[1]
                
            print("\r[info]",worldname, "| 人数 :", player_number, "人 | 滞在時間 :",stay_time[-6:-4] + "時間" + stay_time[-4:-2] + "分" + stay_time[-2:] + "秒", "            ", end="")

            await asyncio.sleep(1)

    async def init_main():
        event_handler = ChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, "./", recursive=False)
        observer.start()

        server = AsyncIOOSCUDPServer((ip, receive_port), dispatcher, asyncio.get_event_loop())
        transport, protocol = await server.create_serve_endpoint()

        await main()

        transport.close()

    asyncio.run(init_main())




