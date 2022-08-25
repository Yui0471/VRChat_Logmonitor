# -*- coding:utf-8 -*-

import os
import sys
import time
import glob
import threading
from pythonosc.udp_client import SimpleUDPClient

moni = """
######################################
#                                    #
#   VRChat Log Monitor               #
#                  Version 3.2.0     #
#                                    #
#   Author : Yui-Kazeniwa            #
#                                    #
######################################

[info] 現在のワールド、インスタンス人数をログから取得します
[Warning!] VRChatを起動してから本スクリプトを実行してください
"""

ip = "127.0.0.1"
port = 9000

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

# 最新のログファイルを取得
def logfile_detection(directory_path):
    files = glob.glob(directory_path + "\\*")

    logfiles = []
    for s in files: # ログファイルのみを抽出
        if "output_log_" in s:
            logfiles.append(s)
        else:
            pass

    if len(logfiles) == 0:
        print("[Error!] ログファイルが見つかりませんでした。VRChatを起動してから実行してください")
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
        print("[info] VRChatディレクトリに移動しました")
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
    for s in data:
        if "Entering Room:" in s:
            world = s # ついでにワールド名も取れる
            worldcount = count # ワールドjoinのログがある行番号を記録
        count += 1 # 行番号をカウント

    if worldcount == 0: # 起動したてでワールド情報がログに出力されていない場合
        for i in range(10, -1, -1):
            print("\r[Error!] ワールド情報が取得できませんでした。{}秒後に再取得します".format(i), end="")
            time.sleep(1)

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


# 経過時間をhhmmssで返す
def elapsed_time_str(seconds):
    seconds = int(seconds + 0.5)
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds - h * 3600 - m * 60

    return f"{h:02}{m:02}{s:02}"

    

if __name__ == "__main__":
    print(moni)
    print("[info] 準備ができたらEnterを押してください")
    input()
    print("[info] ログの監視を開始します")
    print("[info] IP :", ip, "PORT :", port)
    print("[info] OSC送信を開始します")

    client = SimpleUDPClient(ip, port)

    filepath = logfile_detection(directory_move()) # VRChatディレクトリを探してパスを返す

    player_list = [] # プレイヤーリストの保存場所
    world_time_com = ["", 0] # 取得したワールド名と人数の保存場所
    OSC_send_data = { # 送信するOSCパラメータの保存場所
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0,
        8: 0
    }

    while True:
        logdata = txt_open(filepath)
        world = current_world(logdata)

        while world is None: # 取得できないとNoneが返るので再取得
            logdata = txt_open(filepath)
            world = current_world(logdata)

        player_list = player_count(logdata, world[0]) # プレイヤーのリストを取得

        player_number = str(len(player_list)).zfill(2) # プレイヤーの人数(有効数字二桁0埋め)

        # 滞在時間計算部分
        now_time = int(time.time()) # 現在時刻
        # もし記録していたワールド名が現在のワールドと違っているか
        # インスタンス人数が0になったら書き換える
        if world_time_com[0] != world[1] or player_number == 0:
            world_time_com[0] = world[1]
            world_time_com[1] = now_time

        diff = now_time - world_time_com[1] # 差分
        stay_time = elapsed_time_str(diff) # インスタンス滞在時間hhmmss

        send_data = { # 取得したデータを整理して格納
            1: param_dict_first[int(player_number[-2])],
            2: param_dict_second[int(player_number[-1])],
            3: param_dict_third[int(stay_time[-6])],
            4: param_dict_fourth[int(stay_time[-5])],
            5: param_dict_fifth[int(stay_time[-4])],
            6: param_dict_sixth[int(stay_time[-3])],
            7: param_dict_seventh[int(stay_time[-2])],
            8: param_dict_eighth[int(stay_time[-1])]
        }

        for i in range(1, 9): # 前回と比較, 違う値があった場合OSCを送信
            if OSC_send_data[i] != send_data[i]:
                client.send_message("/avatar/parameters/Log_Monitor", send_data[i])
                time.sleep(0.3)

        # OSCで送信したデータを保存
        for key in OSC_send_data.keys():
            OSC_send_data[key] = send_data[key]

        print("\r[info]",world[1], "| 人数 :", player_number, "人 | 滞在時間 :",stay_time[-6:-4] + "時間" + stay_time[-4:-2] + "分" + stay_time[-2:] + "秒", "            ", end="")

        # time.sleep()


