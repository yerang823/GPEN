# +
import os
import glob
import click
from moviepy.editor import *

@click.command()
@click.option('--pics', 'pics', help='Target image folder to project to', required=True, metavar='DIR')
@click.option('--output_folder', help='Where to save the output images', required=True, metavar='DIR')
def main(pics, output_folder):
    
    os.makedirs(f'{output_folder}',exist_ok=True)
    
    for folder_path in glob.glob(f'{pics}/*'): #./jtbc_output_img_sim

        files=[]
        li = glob.glob(folder_path+'/*_GPEN.jpg')
        li.sort()
        for i in li:
            files.append(i)

        folder_name = folder_path.split('/')[-1]
        clip = ImageSequenceClip(files, fps = 30)
        clip.write_videofile(f'{output_folder}/{folder_name}.mp4') #./jtbc_output_mp4_sim


# -

if __name__ == '__main__':
    main()
