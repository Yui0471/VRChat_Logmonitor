# -*- coding:utf-8 -*-

import os
import sys
import time
import glob
from pythonosc.udp_client import SimpleUDPClient

moni = """
############################################
#                                          #
#   VRChat Log Monitor                     #
#                  Version Alpha 1.1.0     #
#                                          #
#   Author : Yui-Kazeniwa                  #
#                                          #
############################################

[info] 現在のワールド、インスタンス人数をログから取得します
[!Warning!] VRChatを起動してから本スクリプトを実行してください
"""

ip = "127.0.0.1"
port = 9000

# 最新のログファイルを取得
def logfile_detection(directory_path):
    files = glob.glob(directory_path + "\\*")

    logfiles = []
    for s in files: # ログファイルのみを抽出
        if "output_log_" in s:
            logfiles.append(s)
        else:
            pass
    
    latest = max(logfiles, key=os.path.getctime) # 最新のログファイルのパスを取得

    return latest


# ログファイルのある場所まで移動
def directory_move():
    username = os.getlogin()
    directory_path = "C:\\Users\\" + username + "\\Appdata\\LocalLow\\VRChat\\VRChat"
    
    try:
        os.chdir(directory_path)
        # print("[info] VRChatディレクトリに移動しました")
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

    for s in data:
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
    


if __name__ == "__main__":
    print(moni)
    print("[info] 準備ができたらいずれかのキーを押してください")
    input()
    print("[info] ログの監視を開始します")

    print("[info] IP :", ip, "PORT :", port)

    client = SimpleUDPClient(ip, port)

    filepath = logfile_detection(directory_move())
    player_list = []

    try:
        while True:
            logdata = txt_open(filepath)
            world = current_world(logdata)

            player_list = player_count(logdata, world[0])
            player = len(player_list)

            print("\r", "[info] 現在のワールド", world[1], ": 現在のインスタンス人数", player, "人", end="")

            player_str = str(player)

            # 恐らく3桁になることはないはず……。
            if len(player_str) == 1:
                first = player_str[-1] # 一の位
                client.send_message("/avatar/parameter/*", int(first))
            else:
                first = player_str[-1] # 一の位
                second = player_str[-2] # 十の位
                client.send_message("/avatar/parameter/*", int(first))
                client.send_message("/avatar/parameter/**", int(second))

            time.sleep(1)

    except Exception as e:
        print(e)