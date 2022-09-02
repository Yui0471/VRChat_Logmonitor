# -*- coding:utf-8 -*-

import os
import sys
import glob

log = """
######################################
#                                    #
#   VRChat Log Monitor               #
#        OSC File Deleter v 0.0.0    #
#                                    #
######################################

[info] VRChatファイル内のOSCデータを削除します
[Warning!] 削除されたファイルはVRChatによって再生成されます

[info] 開始するにはEnterを押してください
"""

def OSCfile_detection():
    username = os.getlogin()
    directory_path = "C:\\Users\\" + username + "\\Appdata\\LocalLow\\VRChat\\VRChat\\OSC"
    
    try:
        os.chdir(directory_path)
        print("[info] VRChat/OSCディレクトリを発見しました")

    except FileNotFoundError:
        input("[Error!] VRChat/OSCディレクトリが見つかりませんでした")
        sys.exit()

    files = glob.glob(directory_path + "\\*")

    datafiles = []
    for s in files:
        if "usr_" in s:
            for path in glob.glob(s + "\\Avatars\\*"):
                datafiles.append(path)
        else:
            pass

    if not datafiles:
        input("[Error!] ファイルが見つかりませんでした。Enterで終了します")
        sys.exit()

    OSCfiles = []
    for s in datafiles:
        if os.path.splitext(s)[1] == ".json":
            OSCfiles.append(s)

    return OSCfiles
    
def file_deleter(OSCfiles):
    input("[Warning!] OSCファイルの削除を開始するにはEnterを押してください")
    print("[info] OSCファイルの削除を開始します")

    for s in OSCfiles:
        try:
            os.remove(s)
            print("[info]", os.path.basename(s), "を削除しました")
        except FileNotFoundError:
            print("[Error!] ファイルが見つかりませんでした")
        except PermissionError:
            print("[Error!] フォルダは削除できません")

    print("[info] \nOSCファイルの削除を完了しました")
    input("[info] Enterで終了します")

if __name__ == "__main__":
    input(log)

    file_deleter(OSCfile_detection())