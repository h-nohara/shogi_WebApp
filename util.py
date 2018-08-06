#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, glob2, re
import numpy as np
import shogi

'''駒名
'''

PieceNames_normal = [
    "OU", "HI", "KA", "KI", "GI", "KE", "KY", "FU",
    "RY", "UM", "NG", "NK", "NY", "TO"
]

PieceNames_normal_NotNari = ["HI", "KA", "KI", "GI", "KE", "KY", "FU"]


PieceName_normal2kanji = {
    "OU" : "王",
    "HI" : "飛",
    "KA" : "角",
    "KI" : "金",
    "GI" : "銀",
    "KE" : "桂",
    "KY" : "香",
    "FU" : "歩",
    "RY" : "龍",
    "UM" : "馬",
    "NG" : "成銀",
    "NK" : "成桂",
    "NY" : "成香",
    "TO" : "と"
}

PieceName_api2normal= {
    "p" : "FU",
    "l" : "KY",
    "n" : "KE",
    "s" : "GI",
    "g" : "KI",
    "b" : "KA",
    "r" : "HI",
    "k" : "OU",
    "+p" : "TO",
    "+l" : "NY",
    "+n" : "NK",
    "+s" : "NG",
    "+b" : "UM",
    "+r" : "RY"
}

PieceName_normal2api = {normal_name : api_name for api_name, normal_name in PieceName_api2normal.items()}

PieceName_apinumber2normal = {
    1 : "FU", # 歩
    2 : "KY", # 香
    3 : "KE", # 桂
    4 : "GI",# 銀
    5 : "KI", # 金
    6 : "KA", # 角
    7 : "HI",# 飛車
    8 : "OU", # 玉
}



'''盤上の位置
'''

locs_normal = [str(i)+str(j) for j in range(1,10) for i in range(1,10)]


loc_api2normal = {}  # api -> normal

row_num = 0
for i in range(81):
    if i % 9 == 0:
        row_num += 1
    col_num = 9 - (i%9)
    loc_api2normal[i] = str(col_num) + str(row_num)

loc_normal2api = {loc_normal : loc_int for loc_int, loc_normal in loc_api2normal.items()}  # normal -> api


num2alpha = {
    1:"a", 2:"b", 3:"c", 4:"d", 5:"e", 6:"f", 7:"g", 8:"h", 9:"i"
}

alpha2num = {alpha : num for num, alpha in num2alpha.items()}



def loc_normal2usi(loc):
    
    '''
    loc(str) : "2726" or "77" or "22+" or "FU" or "FU55"

    >>> loc_normal2usi("2726")  # 27 -> 26
    '2g2f'
    >>> loc_normal2usi("FU55")  # ５五歩打
    'P*5e'
    >>> loc_normal2usi("22+")  # ２二成
    '2b+'
    '''

    def loc_normal2usi_two_str(loc):
        # "77" -> "7g"
        try:
            int(loc)
            return loc[0] + num2alpha[int(loc[1])]
        # "FU" -> "P*"
        except:
            return PieceName_normal2api[loc].upper() + "*"


    if len(loc) == 2:
        return loc_normal2usi_two_str(loc)
    elif len(loc) == 4:
        return loc_normal2usi_two_str(loc[:2]) + loc_normal2usi_two_str(loc[2:4])
    elif len(loc) == 3:
        assert loc[-1] == "+"  #成り
        return loc_normal2usi_two_str(loc[:2]) + "+"
    elif len(loc) == 5:
        assert loc[-1] == "+"  # 成り
        return loc_normal2usi_two_str(loc[:2]) + loc_normal2usi_two_str(loc[2:4]) + "+"


def loc_usi2normal(loc):
    
    '''
    loc(str) : "2g2f" or "P*5e" or "2b+" or "2c2b+"

    >>> loc_normal2usi("2g2f")  # 27 -> 26
    '2726'
    >>> loc_normal2usi("P*5e")  # ５五歩打
    'FU55'
    >>> loc_normal2usi("2b+")  # ２二成
    '22+'
    '''

    def loc_usi2normal_two_str(loc):
        # 'P*' -> "FU"
        if loc[1] == "*":
            return PieceName_api2normal[loc[0].lower()]
        # '7g' -> '77'
        else:
            return loc[0] + str(alpha2num[loc[1]])

    if len(loc) == 2:
        return loc_usi2normal_two_str(loc)
    elif len(loc) == 4:
        return loc_usi2normal_two_str(loc[:2]) + loc_usi2normal_two_str(loc[2:4])
    elif len(loc) == 3:
        assert loc[-1] == "+"
        return loc_usi2normal_two_str(loc[:2]) + "+"
    elif len(loc) == 5:
        assert loc[-1] == "+"
        return loc_usi2normal_two_str(loc[:2]) + loc_usi2normal_two_str(loc[2:4]) + "+"





def RGBA_to_kivy_format(rgba):
    
    '''
    RGBA_to_kivy_format([255, 104, 255, 0.5])
    '''

    assert isinstance(rgba, list)
    assert(len(rgba)==4)
    RGB = rgba[:-1]
    A = rgba[-1]
    return list(np.array(RGB, dtype=np.float)/255.) + [A]




def get_piece_from_board(board, loc):

    '''
    board(Board インスタンス) : shogi apiのBoardインスタンス
    loc(str) : 位置

    >>> board = Board()
    >>> get_piece_from_board(board, "11")
    (False, 'KY')
    >>> get_piece_from_board(board, "55")
    (None, None)
    '''

    loc_api_format = loc_normal2api[loc]
    piece_obj = board.piece_at(loc_api_format)

    if piece_obj is None:
        return None, None
    else:
        piece_str = piece_obj.symbol()

        # 先手後手判定（大文字なら先手）
        is_sente = False
        if piece_str == piece_str.upper():
            is_sente = True
            piece_str = piece_str.lower()

        piece_name = PieceName_api2normal[piece_str]

        return is_sente, piece_name


def get_pieces_in_hand(board):
    
    pieces_in_hand_sente = {piece : 0 for piece in PieceNames_normal_NotNari}
    pieces_in_hand_gote = {piece : 0 for piece in PieceNames_normal_NotNari}

    for i in range(2):
            
        if i == 0:
            is_sente = True
        elif i == 1:
            is_sente = False
            
        pieces_counter = board.pieces_in_hand[i]
        pieces_apinumber = list(pieces_counter.elements())
        pieces_normal_name = [PieceName_apinumber2normal[name] for name in pieces_apinumber]
        
        for piece_name in pieces_normal_name:
            
            if is_sente:
                pieces_in_hand_sente[piece_name] += 1
            else:
                pieces_in_hand_gote[piece_name] += 1

    return pieces_in_hand_sente, pieces_in_hand_gote