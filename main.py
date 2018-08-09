#!/user/bin/env python 
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
app = Flask(__name__, static_folder="static") #インスタンス生成
app.config['JSON_AS_ASCII'] = False  # 文字化け防ぐ


import os, sys, glob2, subprocess, shutil, copy
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import re
import json

import shogi
from util import get_piece_from_board, get_pieces_in_hand, locs_normal, loc_usi2normal, loc_normal2usi, PieceNames_normal_NotNari, PieceName_normal2kanji

from history_to_images import history_to_images



def decode_to_dict(request):
    receive = request.form
    temp = list(receive.keys())
    json_str = temp[0]
    result_dict = json.loads(json_str, encoding="utf-8")
    return result_dict


def get_LocPieceDict(board):
    
    main_board = get_LocPieceDict_MainBoard(board)
    sub_boards = get_PieceInHand(board)

    return {"main" : main_board, "sub" : sub_boards}



def get_LocPieceDict_MainBoard(board):
        
    '''
    現在の局面（boardインスタンス）の駒位置を画面に反映させる
    '''

    loc_piece_dict = {}
            
    for loc in locs_normal:
        is_sente, piece_name = get_piece_from_board(board, loc)

        if piece_name is not None:
            piece_name = PieceName_normal2kanji[piece_name]  # 漢字表記に
            if not is_sente:
                piece_name = "v" + piece_name
            loc_piece_dict[loc] = piece_name

        else:
            
            loc_piece_dict[loc] = None

    return loc_piece_dict

def get_PieceInHand(board):
    
    '''
    return(dict(dict)) : {"sente" : {"GI":0, ...}, "gote" : {"GI":0, ...}}
    '''
    
    pieces_in_hand = get_pieces_in_hand(board)
    
    result_dict = {"sente" : pieces_in_hand[0], "gote" : pieces_in_hand[1]}
    
    # for i in range(2):
    #     PieceInHand = {key : 0 for key in PieceNames_normal_NotNari}
    #     for piece in pieces_in_hand[0]:
    #         PieceInHand[piece] += 1
    #     if i == 0:
    #         result_dict["sente"] = PieceInHand
    #     else:
    #         result_dict["gote"] = PieceInHand
        
    return result_dict



def get_legal_moves(board, loc):
        
    '''
    locの位置の駒が動ける範囲を表示する

    loc(str) : 動かす駒の元の場所 "55"
    
    return(list(str)) : "56", "77+"
    '''
    
    all_legal_moves = list(board.generate_legal_moves())
    all_legal_moves_usi = [move.usi() for move in all_legal_moves]  # usi形式の文字列で取得
    all_legal_moves_normal = [loc_usi2normal(move) for move in all_legal_moves_usi]  # 標準形式の文字列に

    print(all_legal_moves_normal)

    legal_moves_the_piece_destination = []
    for move in all_legal_moves_normal:
        if move[:2] == loc:
            legal_moves_the_piece_destination.append(move[2:])

    print(legal_moves_the_piece_destination)

    return legal_moves_the_piece_destination


#######################################################


@app.route("/")
def board_view():
    
    global BOARD
    BOARD = shogi.Board()

    global BOARD_HISTORY
    BOARD_HISTORY = [copy.deepcopy(BOARD)]

    return render_template("gui.html")



@app.route("/get_board")
def get_board():
    
    global BOARD
    print("get_baord received")
    
    # 盤面を送る
    loc_piece_dict = get_LocPieceDict(BOARD)
    return jsonify(loc_piece_dict)


@app.route("/get_legal_moves/<loc>", methods=["POST"])
def get_legal_moves_destination(loc):
    
    '''
    return(str) : "77,88+,99+"
    '''

    global BOARD
    
    legal_moves = get_legal_moves(BOARD, loc)
    legal_moves = ",".join(legal_moves)

    return legal_moves


@app.route("/push/<start_loc>/<dest_loc>")
def push_and_send_board(start_loc, dest_loc):
    
    global BOARD
    
    # push
    BOARD.push_usi(loc_normal2usi(start_loc) + loc_normal2usi(dest_loc))

    # 盤面を送る
    loc_piece_dict = get_LocPieceDict(BOARD)

    return jsonify(loc_piece_dict)


@app.route("/memorize_board_history")
def memorize_board_history():
    
    global BOARD_HISTORY
    BOARD_HISTORY.append(copy.deepcopy(BOARD))
    print(BOARD_HISTORY)

    return "hoge"


@app.route("/fly_to/<history_order>")
def fly_to(history_order):
    
    print("receiving fly_to")
    global BOARD
    global BOARD_HISTORY
    BOARD = copy.deepcopy(BOARD_HISTORY[int(history_order)])

    return "hoge"


# BOARD_HISTORYを特定の箇所以降を削除する
@app.route("/update_board_history/<del_number>")
def update_board_history(del_number):
    
    global BOARD_HISTORY
    BOARD_HISTORY = BOARD_HISTORY[:int(del_number)]
    global BOARD
    BOARD = BOARD_HISTORY[-1]

    return "hoge"



# HistoryをJSから受け取り、それを元に画像を生成する
@app.route("/make_images_from_history", methods=["POST"])
def make_images_from_history():

    print("="*10)
    history = decode_to_dict(request)

    # なぜかmoveの「＋」が抜けてしまうので、対策
    for i in range(len(history)):
        one_action = history[i]
        if "move" in one_action.keys():
            if len(one_action["move"]) == 5:
                history[i]["move"] = history[i]["move"][:4] + "+"
                
    save_dir = "./testing/"
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir)

    global BOARD_HISTORY
    history_to_images(history, BOARD_HISTORY, save_dir)

    return "hoge"


    
    
if __name__ == "__main__":
    
    app.run(host="localhost", port=8090, debug=True)
