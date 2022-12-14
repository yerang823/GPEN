# enhance faces
import glob
import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
import __init_paths
from face_enhancement import FaceEnhancement
import click
from pathlib import Path
import tqdm

def faceEnhance(img, filename='output.jpg', outdir='sr_output', sr_scale=4, tile_size=32, verbose=False):
    model = {'name':'GPEN-BFR-512', 'sr_model':'realesrnet', 'sr_scale': sr_scale, 'size':512, 'channel_multiplier':2, 'narrow':1}
    # outdir = 'examples/outs-bfr'
    os.makedirs(outdir, exist_ok=True)
    faceenhancer = FaceEnhancement(in_size=model['size'], model=model['name'], use_sr=False, sr_model=model['sr_model'], sr_scale=model['sr_scale'], tile_size=tile_size, channel_multiplier=model['channel_multiplier'], narrow=model['narrow'])
    img_out, orig_faces, enhanced_faces = faceenhancer.process(img, aligned=False)
    img = cv2.resize(img, img_out.shape[:2][::-1])
    if verbose:
        cv2.imwrite(os.path.join(outdir, '.'.join(filename.split('.')[:-1])+'_COMP.jpg'), np.hstack((img, img_out)))
        for m, (ef, of) in enumerate(zip(enhanced_faces, orig_faces)):
            of = cv2.resize(of, ef.shape[:2])
            cv2.imwrite(os.path.join(outdir, '.'.join(filename.split('.')[:-1])+'_face%02d'%m+'.jpg'), np.hstack((of, ef)))
    cv2.imwrite(os.path.join(outdir, '.'.join(filename.split('.')[:-1])+'_GPEN.jpg'), img_out)

    return img_out

@click.command()
@click.option('--target', 'target_fnames', help='Target image folder to project to', required=True, metavar='DIR')
@click.option('--outdir', help='Where to save the output images', required=True, metavar='DIR')
@click.option('--sr_scale', type=int, default=4, help='SR scale parameter for model.')
@click.option('--tile_size', type=int, default=64, help='Tile size for SR model.')
@click.option('--verbose', '-v', is_flag=True, help="Print more output.")
def run_faceEnhance(target_fnames, outdir, sr_scale, tile_size, verbose):
    for target_fname in tqdm.tqdm(Path(target_fnames).glob('*')):
        target = cv2.imread(str(target_fname))
        faceEnhance(target, target_fname.name, outdir, sr_scale, tile_size, verbose)
        print(f'Finish {target_fname}')

if __name__ == '__main__':
    print('start!')
    run_faceEnhance()



# +
# @click.command()
# @click.option('--target', 'target_fnames', help='Target image folder to project to', required=True, metavar='DIR')
# @click.option('--outdir', help='Where to save the output images', required=True, metavar='DIR')
# @click.option('--sr_scale', type=int, default=4, help='SR scale parameter for model.')
# @click.option('--tile_size', type=int, default=64, help='Tile size for SR model.')
# @click.option('--verbose', '-v', is_flag=True, help="Print more output.")
# def run_faceEnhance(target_fnames, outdir, sr_scale=4, tile_size=64, verbose=False):
#     for target_fname in tqdm.tqdm(Path(target_fnames).glob('*')):
#         target = cv2.imread(str(target_fname))
#         faceEnhance(target, target_fname.name, outdir, sr_scale, tile_size, verbose)
#         print(f'Finish {target_fname}')

# +
# if __name__ == '__main__':
#     target_li = glob.glob('../sber-swap/jtbc_output_img/*_unknown')
#     for t_dir in target_li:
        
#         print('============================================')
#         print(t_dir)
#         print('============================================')
        
#         name = t_dir.split('/')[-1]
#         if name == 'kjy_unknown':
#             continue
        
#         output_dir = './jtbc_output_img/{}'.format(name)
#         if not Path(output_dir).is_dir():
#             Path(output_dir).mkdir()
#         run_faceEnhance(target_fnames = t_dir, outdir = output_dir)
