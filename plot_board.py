#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, glob2, re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.image as mpimg

PIECE_SYMBOLS_DICT = {
    "p" : "歩",
    "l" : "香",
    "n" : "桂",
    "s" : "銀",
    "g" : "金",
    "b" : "角",
    "r" : "飛",
    "k" : "玉",
    "+p" : "と",
    "+l" : "杏",
    "+n" : "圭",
    "+s" : "全",
    "+b" : "馬",
    "+r" : "龍"
}

SQUARES = [
    A9, A8, A7, A6, A5, A4, A3, A2, A1,
    B9, B8, B7, B6, B5, B4, B3, B2, B1,
    C9, C8, C7, C6, C5, C4, C3, C2, C1,
    D9, D8, D7, D6, D5, D4, D3, D2, D1,
    E9, E8, E7, E6, E5, E4, E3, E2, E1,
    F9, F8, F7, F6, F5, F4, F3, F2, F1,
    G9, G8, G7, G6, G5, G4, G3, G2, G1,
    H9, H8, H7, H6, H5, H4, H3, H2, H1,
    I9, I8, I7, I6, I5, I4, I3, I2, I1,
] = range(81)

PATH_MATERIALS = "./pyogi-develop/pyogi/materials/"
csa_to_code = {
    'OU': 1, 'HI': 2, 'KA': 3, 'KI': 4, 'GI': 5,
    'KE': 6, 'KY': 7, 'FU': 8, 'RY': 22, 'UM': 23,
    'NG': 25, 'NK': 26, 'NY': 27, 'TO': 28
}


shogiapi_to_code = {
    "P" : csa_to_code["FU"], # 歩
    "L" : csa_to_code["KY"], # 香
    "N" : csa_to_code["KE"], # 桂
    "S" : csa_to_code["GI"],# 銀
    "G" : csa_to_code["KI"], # 金
    "B" : csa_to_code["KA"], # 角
    "R" : csa_to_code["HI"],# 飛車
    "K" : csa_to_code["OU"], # 玉
    
    "+R" : csa_to_code["RY"], # 龍
    "+B" : csa_to_code["UM"], # 馬
    "+S" : csa_to_code["NG"],  # 成銀
    "+N" : csa_to_code["NK"],  # 成桂
    "+L" : csa_to_code["NY"],  # 成香
    "+P" : csa_to_code["TO"] # と
}

shogicode_to_code = {
    1 : csa_to_code["FU"], # 歩
    2 : csa_to_code["KY"], # 香
    3 : csa_to_code["KE"], # 桂
    4 : csa_to_code["GI"],# 銀
    5 : csa_to_code["KI"], # 金
    6 : csa_to_code["KA"], # 角
    7 : csa_to_code["HI"],# 飛車
    8 : csa_to_code["OU"], # 玉
}

num2alpha = {
    1:"a", 2:"b", 3:"c", 4:"d", 5:"e", 6:"f", 7:"g", 8:"h", 9:"i"
}

PieceName_Util2Csa = {
    "FU" : "P", # 歩
    "KY" : "L", # 香
    "KE" : "N", # 桂
    "GI" : "S",# 銀
    "KI" : "G", # 金
    "KA" : "B", # 角
    "HI" : "R",# 飛車
    "OU" : "K", # 玉
    
    "RY" : "+R", # 龍
    "UM" : "+B", # 馬
    "NG" : "+S",  # 成銀
    "NK" : "+N",  # 成桂
    "NY" : "+L",  # 成香
    "TO" : "+P" # と
}

def numnum2csa(move):
    '''
    move(str) : "7776", "7733+", "KA55"

    >>> numnum2csa("7776+")  # 7六成り
    '7g7f+'
    >>> numnum2csa(HI55)  # 5五飛打ち
    'R*5e'
    '''
    
    if not ((len(move) == 4) or (len(move) == 5)):
        raise ValueError("not correct arg")
    
    loc_before = move[:2]
    loc_after = move[2:4]
    
    try:
        int(loc_before)
        loc_before_csa = loc_before_csa = loc_before[0] + num2alpha[int(loc_before[1])]
    except:
        loc_before_csa = PieceName_Util2Csa[loc_before] + "*"
        
    
    try:
        int(loc_after)
        loc_after_csa = loc_after[0] + num2alpha[int(loc_after[1])]
    except:
        raise ValueError("the format is not correct")

    
    
    loc_csa = loc_before_csa + loc_after_csa
        
    if len(move) == 5:
        assert move[-1] == "+"
        loc_csa = loc_csa + "+"
        
    return loc_csa




class Plot:
    
    def __init__(self, board):
        
        fig = plt.figure(figsize=(8, 8))

        gs = gridspec.GridSpec(2, 2, width_ratios=[3, 1], height_ratios=[1, 1])
        plt.subplots_adjust(wspace=0.05, hspace=0.05)

        self.ax1 = plt.subplot(gs[0:2, 0])
        self.ax20 = plt.subplot(gs[0, 1])
        self.ax21 = plt.subplot(gs[1, 1])

        # Initialize subplots
        for ax in [self.ax1, self.ax20, self.ax21]:
            ax.tick_params(
                labelleft='off', labelbottom='off',
                bottom='off', top='off', left='off', right='off'
            )
            
        self.board = board
        
    def plot_board(self):
        
        path_jpg = os.path.join(PATH_MATERIALS, 'japanese-chess-b02.jpg')
        img = mpimg.imread(path_jpg)

        self.ax1.imshow(img, extent=[0, 10, 0, 10])
        
    def plot_pieces(self):
        
        row_num = 0
        for i in range(81):
            if i % 9 == 0:
                row_num += 1
            col_num = 9 - (i%9)

            piece_obj = self.board.piece_at(i)

            if piece_obj is None:
                continue
            else:
                piece_str = piece_obj.symbol()

                # 先手後手判定（小文字なら後手）
                is_gote = False
                if piece_str.lower() == piece_str:
                    is_gote = True
                    piece_str = piece_str.upper()

                self._plot_one_piece(loc=(col_num, row_num), piece_str=piece_str, is_gote=is_gote)

    
    def _plot_one_piece(self, loc, piece_str, is_gote):

        '''
        loc(tuple) : location of the koma
        is_gote(bool)
        '''

        koma_code = is_gote*30 + shogiapi_to_code[piece_str]

        fname = 'sgl{0:02}.png'.format(koma_code)
        path_koma = os.path.join(PATH_MATERIALS, fname)
        img_koma = mpimg.imread(path_koma)

        self.ax1.autoscale(False)
        x, y = 0.5 + (9 - loc[0]), 0.5 + (9 - loc[1])
        self.ax1.imshow(img_koma, extent=[x, x+1, y, y+1])
        
        
        
    def plot_komadai(self):
        fname = 'japanese-chess-bg.jpg'
        path = os.path.join(PATH_MATERIALS, fname)
        img = mpimg.imread(path)

        axes = [self.ax21, self.ax20]
        for ax in axes:
            ax.autoscale(False)
            ax.imshow(img, extent=[0, 5, 0, 5])
            
            
            
    def plot_mochigoma(self):
        
        n_sente_mochigoma = 0
        n_gote_mochigoma = 0

        axes = [self.ax21, self.ax20]
        
        piece_code = csa_to_code["FU"]
    
        
        is_gote = True
        
        for i in range(2):
            
            if i == 0:
                is_gote = False
            elif i == 1:
                is_gote = True
                
            pieces_counter = self.board.pieces_in_hand[i]
            pieces = list(pieces_counter.elements())
            
            for piece_code in pieces:
                
                piece_code = shogicode_to_code[piece_code]

                koma_code = 30*is_gote + piece_code
                fname = 'sgl{0:02}.png'.format(koma_code)
                path_koma = os.path.join(PATH_MATERIALS, fname)
                img_koma = mpimg.imread(path_koma)
                axes[is_gote].autoscale(False)

                N_COLUMN = 9

                if not is_gote:
                    x = 0.1 * float(n_sente_mochigoma % N_COLUMN)
                    y = 0.2 * float(n_sente_mochigoma // N_COLUMN)
                else:
                    x = 0.1 * float(n_gote_mochigoma % N_COLUMN)
                    y = (1 - 0.25) - 0.2 * float(n_gote_mochigoma // N_COLUMN)

                axes[is_gote].imshow(img_koma, extent=[x, x+1/5, y, y+1/5])

                n_sente_mochigoma += not is_gote
                n_gote_mochigoma += is_gote
                
                
                
    def plot_haikei(self, locs, shape="square"):
        
        '''
        locs(list(tuple))
        
        >>> self.plot_haikei(locs=[(3,4), (5,5)])  # 3四と5五
        '''
        
        for loc in locs:
        
            if shape == "square":
                img_path = "./test.png"
                alpha = 0.5
            elif shape == "circle":
                img_path = "./circle.png"
                alpha = 1
            img = mpimg.imread(img_path)

            self.ax1.autoscale(False)
            x, y = 0.5 + (9 - loc[0]), 0.5 + (9 - loc[1])
            self.ax1.imshow(img, extent=[x+0.05, x+1-0.05, y+0.1, y+1], alpha=alpha)
        
                
                
    def plot_hoge(self):
        
        loc = (4, 5)
        
        img_path = "./test.png"
        img = mpimg.imread(img_path)

        self.ax1.autoscale(False)
        x, y = 0.5 + (9 - loc[0]), 0.5 + (9 - loc[1])
        self.ax1.imshow(img, extent=[x+0.05, x+1-0.05, y+0.1, y+1], alpha=0.5)
        
        
    def plot_all(self):
        self.plot_board()
        self.plot_haikei(locs=[(4, 5), (7, 7)])
        self.plot_pieces()
        self.plot_komadai()
        self.plot_mochigoma()
        plt.show()
        
    def save_pic(self, fname):
        
        plt.savefig(fname, bbox_inches="tight", pad_inches=0)