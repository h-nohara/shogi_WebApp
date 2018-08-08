#!/user/bin/env python 
# -*- coding: utf-8 -*-

import subprocess

adding = '"scale=trunc(iw/2)*2:trunc(ih/2)*2"'

concat_cmd = "ffmpeg -y -r 1 -i testing/img_%03d.png -vcodec libx264 -pix_fmt yuv420p -r 2 -vf {} testing.mp4".format(adding)

subprocess.call(concat_cmd, shell=True)
