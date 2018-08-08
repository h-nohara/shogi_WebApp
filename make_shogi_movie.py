#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys, copy
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from plot_board import Plot
from image_handlers.make_WordImage import make_WordImage
from image_handlers.overlaid_image import overlaid_handler


def alpha2num(x):
    '''
    小文字のアルファベットを数字に変換

    >>> alpha2num("c")
    3
    '''
    return ord(x) - ord("a") + 1


class Scenario:
    
    def __init__(self, board=None, actions=[], save_dir=None, is_main=True):
        

        '''
        board : これがメインシナリオならインスタンス化の際に指定、サブシナリオならNoneにすると、親のシナリオの際の棋譜が代入される
        actions(list(Action))
        '''
        
        self.board = copy.deepcopy(board)
        self.actions = actions
        self.save_dir = save_dir
        self.is_main = is_main

        if self.is_main:
            assert self.save_dir is not None
            self.PicRecorder = PicRecorder(self.save_dir)  # 保存画像のレコーダを作成
            self.StateRecorder = StateRecorder()  # 盤面のレコーダを作成
        

        for action in self.actions:
            action.parent_scenario = self

        self.action_pos = 0

    def next(self):
        
        if self.board is None:
            raise ValueError("set self.board")
        
        self.actions[self.action_pos]()
        self.action_pos += 1

    def do_all(self):
        for _ in range(len(self.actions)):
            self.next()




class Action:

    def __init__(self, move_CsaFormat=None, fly_to=None, scenario=None, message=None, id_=None, to_save_pic=True):
        
        '''
        どれか１つだけを設定する

        move_CsaFormat(str) : 「7g7f」のような表記
        fly_to(str or int)
        scenario(Scenario)
        message(Message)
        id_(str or int) : このアクション後の盤面の状態を記録しておく
        tp_save_pic(bool) : このアクション後の盤面の画像を保存するか
        '''

        self.move = move_CsaFormat
        self.fly_to = fly_to
        self.scenario = scenario
        self.message = message
        self.to_save_pic = to_save_pic
        self.id_ = id_

        # どれか１つのアクションだけが引数で与えられているかチェックする
        n_not_none = 0
        for param in [self.move, self.fly_to, self.scenario, self.message, self.id_]:
            if param is not None:
                n_not_none += 1
        if n_not_none != 1:
            raise ValueError("set only one action param")

        # サブシナリオになっているかどうかチェック
        if self.scenario:
            if self.scenario.is_main:
                raise("set the param is_main - False")
        
        self.parent_scenario = None



    def __call__(self):
        
        # 駒を動かす

        if self.move:
            self.parent_scenario.board.push_usi(self.move)  # 指し手を実行して盤面に反映
            
        # 特定の局面へ移動 : todo

        elif self.fly_to:
            self.parent_scenario.board = self.parent_scenario.StateRecorder[self.fly_to]
        
        # 子シナリオを実行 : todo

        elif self.scenario:
            
            # もしボードが指定されていなかったら、現在の局面のコピーを使用
            if self.scenario.board is None:
                self.scenario.board = copy.deepcopy(self.parent_scenario.board)
            
            # 親のレコーダーを引き継ぐ
            self.scenario.PicRecorder = self.parent_scenario.PicRecorder
            self.scenario.StateRecorder = self.parent_scenario.StateRecorder

            self.scenario.do_all()  # サブシナリオを実行
            
        # 画像に注釈等をつける

        elif self.message:
            self.message.parent_action = self
            self.message.draw_all()  # 説明を付け加えた画像を保存


        # 最後に、現在の局面画像を保存

        if self.to_save_pic:

            if self.fly_to or self.scenario:
                self.draw_boad()

            elif self.move:
                pos_after = self.move[2:]  # 動き先の位置
                assert (len(pos_after) == 2) or ((len(pos_after) == 3) and pos_after[-1]=="+")
                self.draw_boad(light_up_locs=[(int(pos_after[0]), alpha2num(pos_after[1]))])

            # もしself.id_が与えられていたら、その名前で現在の局面を保存
            if self.id_ is not None:
                self.parent_scenario.StateRecorder[self.id_] = copy.deepcopy(self.parent_scenario.board)

    
    def draw_boad(self, light_up_locs=False):
        
        '''
        盤面画像を保存する
        オプションで背景に色をつける

        light_up_locs(list(tuple)) : 背景に色をつける位置

        >>> self.draw_board(light_up_locs=[(5,5), (3,4)])
        '''
        
        board_now = self.parent_scenario.board
        board_plot = Plot(board_now)

        board_plot.plot_board()
        if light_up_locs:
            board_plot.plot_haikei(locs=light_up_locs)
        board_plot.plot_pieces()
        board_plot.plot_komadai()
        board_plot.plot_mochigoma()

        save_name = self.parent_scenario.PicRecorder.generate_save_name()
        board_plot.save_pic(save_name)  # 保存
        plt.close()

            


class Message:

    def __init__(self, text=None, light_up_locs=None, mark_locs=None):
        
        '''
        >>> msg = Message(text="この局面", light_up_locs={"locs":[(7,7), (5, 6)], "colors":["pink", "pink"]})
        '''
        
        self.text = text
        self.light_up_locs = light_up_locs
        self.mark_locs = mark_locs

        self.parent_action = None
        self.board_copy = None


    def draw_all(self):
        
        if self.parent_action is None:
            raise ValueError("set self.parent_action")

        # 現在の棋譜をコピーしてくる
        self.board_copy = copy.deepcopy(self.parent_action.parent_scenario.board)

        # 最新の盤面と背景を保存
        if self.light_up_locs or self.mark_locs:

            if self.light_up_locs:
                light_up_locs = self.light_up_locs["locs"]
            else:
                light_up_locs = None

            if self.mark_locs:
                mark_locs = self.mark_locs["locs"]
            else:
                mark_locs = None

            self.draw_boad(light_up_locs=light_up_locs, mark_locs=mark_locs)
        else:
            self.draw_boad()
        
        # 保存した画像にテキストを加えて保存
        if self.text:
            self.draw_text()


    # def draw_floatens(self, pic_name):
        
    #     plt_shogi = Plot(self.board_copy)

    #     plt_shogi.plot_board()
    #     plt_shogi.plot_haikei(locs=self.floatens["locs"])
    #     plt_shogi.plot_pieces()
    #     plt_shogi.plot_komadai()
    #     plt_shogi.plot_mochigoma()

    #     plt_shogi.save_pic(pic_name)

    #     return pic_name


    def draw_boad(self, light_up_locs=False, mark_locs=False):
        
        '''
        盤面画像を保存する
        オプションで背景に色をつける

        light_up_locs(list(tuple)) : 背景に色をつける位置

        >>> self.draw_board(light_up_locs=[(5,5), (3,4)], mark_locs=[])
        '''
        
        board_plot = Plot(self.board_copy)

        board_plot.plot_board()
        if light_up_locs:
            board_plot.plot_haikei(locs=light_up_locs, shape="square")
        # ここ付け加えた！
        if mark_locs:
            board_plot.plot_haikei(locs=mark_locs, shape="circle")
        board_plot.plot_pieces()
        board_plot.plot_komadai()
        board_plot.plot_mochigoma()

        save_name = self.parent_action.parent_scenario.PicRecorder.generate_save_name()
        board_plot.save_pic(save_name)  # 保存
        plt.close()


    # todo : 複数の文字画像を扱えるようにする
    def draw_text(self):
        
        # 最初に文字画像を生成

        save_dir = self.parent_action.parent_scenario.PicRecorder.save_dir
        word_image_path = os.path.join(save_dir, "word_image.png")

        font_size = 50

        make_WordImage(
            word = self.text, 
            fontsize = font_size, 
            fontfile = "/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc", 
            num_color = 3, 
            colors = ["blue", "white", "blue"], 
            stroke_ws = [9 ,3], 
            result_image = word_image_path,
            W = font_size * (1 + len(self.text)),
            H = font_size * 1.3
        )


        # 盤面画像に貼り付ける

        board_image_path = self.parent_action.parent_scenario.PicRecorder.get_latest_name()

        overlaid_handler(board_image_path, [word_image_path], board_image_path)
        
    
    
    
    
class PicRecorder:
    
    def __init__(self, save_dir):
                
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            raise ValueError("{} does'nt exists".format(save_dir))

        self.n_saved = 0  # 保存された画像の数、次に保存する画像のidナンバー
        
    def generate_save_name(self):
        
        '''
        次に保存する画像名を返し、情報をアップデート
        '''

        save_name = os.path.join(self.save_dir, "img_{0:03d}.png".format(self.n_saved))
        self.n_saved += 1
        return save_name

    def get_latest_name(self):
        
        '''
        最新の保存画像名を返す
        '''

        return os.path.join(self.save_dir, "img_{0:03d}.png".format(self.n_saved-1))


class StateRecorder:

    def __init__(self):

        self.id_board_dict = {}

    
    def __setitem__(self, id_, board):

        '''
        board(Board)
        '''

        if id_ in list(self.id_board_dict.keys()):
            raise("the id name of '{}' is already used".format(id_))

        self.id_board_dict[id_] = board

    def __getitem__(self, id_):
        
        return self.id_board_dict[id_]
