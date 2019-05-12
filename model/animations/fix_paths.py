import glob
import os
import os.path as op
import pdb
from pathlib import Path

model_dir = str(Path(op.abspath(__file__)).parents[1])
anim_dir = op.join(os.getcwd(), 'phrase_1')

front_path = op.join(model_dir, 'mask_front.png')
back_path = op.join(model_dir, 'mask_back.png')

# mtl_files = os.listdir(op.join(anim_dir, '*.mtl'))
mtl_files = glob.glob(op.join(anim_dir, '*.mtl'))
for i, mtl in enumerate(mtl_files):
    fpath = op.join(anim_dir, op.basename(mtl))

    with open(fpath, 'r') as fp:
        lines = fp.readlines()
    os.remove(fpath)

    lines[12] = 'map_Kd ' + front_path + '\n'
    lines[23] = 'map_Kd ' + back_path + '\n'

    with open(fpath, 'w') as fp:
        for line in lines:
            fp.write(line)
