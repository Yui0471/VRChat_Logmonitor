# -*- coding:utf-8 -*-

import os
import sys
import time
import glob
from pythonosc.udp_client import SimpleUDPClient

moni = """
######################################
#                                    #
#   VRChat Log Monitor               #
#                  Version 3.0.1     #
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


# 現在のワールド名を基にインスタンスの滞在時間を計算
def time_comparison(worldname, worldpeople):
    now_time = int(time.time()) # 現在時刻

    if world_time_com[0] != worldname or worldpeople == 0: # もし記録していたワールド名が現在のワールドと違っているか、インスタンス人数が0になったら書き換える
        world_time_com[0] = worldname
        world_time_com[1] = now_time

    diff = now_time - world_time_com[1] # 差分

    hour = (diff % (3600 * 24)) // 3600 # 時間計算
    minute = (diff % 3600) // 60
    second = diff % 60

    print_stay_time = ""
    if hour != 0:
        print_stay_time += str(hour) + "時間"
    if minute != 0:
        print_stay_time += str(minute) + "分"
    if second != 0:
        print_stay_time += str(second) + "秒"

    if len(str(hour)) == 1:
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_third[0])
        time.sleep(0.3)
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_fourth[hour])
        time.sleep(0.3)
    else:
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_third[(hour//10)%10])
        time.sleep(0.3)
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_fourth[hour%10])
        time.sleep(0.3)
    if len(str(minute)) == 1:
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_fifth[0])
        time.sleep(0.3)
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_sixth[minute])
        time.sleep(0.3)
    else:
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_fifth[(minute//10)%10])
        time.sleep(0.3)
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_sixth[minute%10])
        time.sleep(0.3)
    if len(str(second)) == 1:
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_seventh[0])
        time.sleep(0.3)
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_eighth[second])
        time.sleep(0.3)
    else:
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_seventh[(second//10)%10])
        time.sleep(0.3)
        client.send_message("/avatar/parameters/Log_Monitor", param_dict_eighth[second%10])
        time.sleep(0.3)


    return print_stay_time
    

if __name__ == "__main__":
    print(moni)
    print("[info] 準備ができたらEnterを押してください")
    input()
    print("[info] ログの監視を開始します")
    print("[info] IP :", ip, "PORT :", port)
    print("[info] OSC送信を開始します")

    client = SimpleUDPClient(ip, port)

    filepath = logfile_detection(directory_move())
    player_list = []
    world_time_com = ["", 0]

    while True:
        logdata = txt_open(filepath)
        world = current_world(logdata)

        while world is None: # 取得できないとNoneが返るので再取得
            logdata = txt_open(filepath)
            world = current_world(logdata)

        player_list = player_count(logdata, world[0])
        player = len(player_list)

        stay_time = time_comparison(world[1], player)

        print("\r[info]",world[1], "| 人数 :", player, "人 | 滞在時間 :",stay_time, end="")

        player_str = str(player)

        # 恐らく3桁になることはないはず……。
        if len(player_str) == 1:
            first = player_str[-1] # 一の位
            client.send_message("/avatar/parameters/Log_Monitor", param_dict_second[int(first)])
            time.sleep(0.3)
            client.send_message("/avatar/parameters/Log_Monitor", param_dict_first[0])
        else:
            first = player_str[-1] # 一の位
            second = player_str[-2] # 十の位
            client.send_message("/avatar/parameters/Log_Monitor", param_dict_second[int(first)])
            time.sleep(0.3)
            client.send_message("/avatar/parameters/Log_Monitor", param_dict_first[int(second)])

        time.sleep(0.3)
