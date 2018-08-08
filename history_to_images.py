#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shogi
import shogi.CSA


from plot_board import numnum2csa
from make_shogi_movie import Action, Message, Scenario


def history_to_images(history, save_dir):
    
    reveived_history = history
    print(history)


    # Boardオブジェクト
    board = shogi.Board()
    print(board)

    actions = []
    
    for one_action in reveived_history:
        
        print(one_action)
        
        keys = list(one_action.keys())

        if "move" in keys:
            
            move_str = one_action["move"]

            if move_str == "initial":
                continue
            
            actions.append(Action(move_CsaFormat=numnum2csa(move_str)))

        elif "message" in keys:
            
            # 全てのキーを用意し、値がなかったらNoneを代入する
            message_all_keys = ["text", "light_up", "mark"]
            for key in message_all_keys:
                if key not in list(one_action["message"].keys()):
                    one_action["message"][key] = None
                elif (one_action["message"][key] == "") or (one_action["message"][key] == [""]):
                    one_action["message"][key] = None


            print(one_action)

            the_message_obj = Message()

            if one_action["message"]["text"] is not None:
                the_message_obj.text = one_action["message"]["text"]

            locs = one_action["message"]["light_up"]
            if locs is not None:
                try:
                    locs = [(int(loc[0]), int(loc[1])) for loc in locs]
                except:
                    print("8"*20)
                    print(locs)
                the_message_obj.light_up_locs = {"locs" : locs}

            locs = one_action["message"]["mark"]
            if locs is not None:
                try:
                    locs = [(int(loc[0]), int(loc[1])) for loc in locs]
                except:
                    print("8"*20)
                    print(locs)
                the_message_obj.mark_locs = {"locs" : locs}

            
            print("{} : {}".format("text", the_message_obj.text))
            print("{} : {}".format("light_up", the_message_obj.light_up_locs))
            print("{} : {}".format("mark", the_message_obj.mark_locs))
            
            actions.append(Action(message=the_message_obj))


    sc = Scenario(board=board, actions=actions, save_dir=save_dir)  # メインシナリオ

    # シナリオに従って、各局面を画像で保存
    sc.do_all()