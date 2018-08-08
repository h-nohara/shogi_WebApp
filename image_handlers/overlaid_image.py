#!/user/bin/env python 
# -*- coding: utf-8 -*-

import os, sys
from PIL import Image


def overlaid_handler(img_back, imgs_for, save_path):
    
    '''
    img_back(str)
    imgs_for(list(str))
    '''

    # 読み込み
    img_back = Image.open(img_back)
    imgs_for = [Image.open(img_for) for img_for in imgs_for]

    # todo
    if len(imgs_for) > 1:
        sys.exit()

    else:
        poss = [get_center_bottom(img_back, imgs_for[0], 40)]

    # 貼り付けて保存
    img_result = overlaid_png(img_back, imgs_for, poss)
    img_result.save(save_path)



# 画像に複数のpng画像を貼り付ける
def overlaid_png(img_back, imgs_for, poss):
    
    if isinstance(img_back, str):
        img_back = Image.open(img_back)
    img_back = img_back.convert("RGBA")  # 元の画像がグレースケールだった時のため
    
    for img_for, pos in zip(imgs_for, poss):
        if isinstance(img_for, str):
            img_for = Image.open(img_for)
        img_back.paste(img_for, pos, mask=img_for.split()[-1])
    
    return img_back


def get_center_bottom(back, forward, y_ext=0):
    
    '''
    back(Imageオブジェクト)
    forward(Imageオブジェクト)
    y_ext(float) : 底辺からの高さs
    '''

    pos_x = int((back.size[0] - forward.size[0]) / 2)
    pos_y = int(back.size[1] - forward.size[1] - y_ext)

    return pos_x, pos_y

