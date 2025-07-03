import os
from glob import glob
from datetime import datetime
import random
from tqdm import tqdm
from pathlib import Path
import yaml
import json

import argparse

from assets.garment_programs.meta_garment import MetaGarment
from assets.bodies.body_params import BodyParameters
from pygarment.data_config import Properties

_BODY_MEASUREMENTS = {
    # Our model
    'neutral': './assets/bodies/mean_all.yaml',
    'mean_female': './assets/bodies/mean_female.yaml',
    'mean_male': './assets/bodies/mean_male.yaml',

    # SMPL
    'f_smpl': './assets/bodies/f_smpl_average_A40.yaml',
    'm_smpl': './assets/bodies/m_smpl_average_A40.yaml',

}


def _parse_file_path(filepath, fmt='*.yaml'):
    if os.path.isfile(filepath): return [filepath]
    elif os.path.isdir(filepath):
        return glob(os.path.join(filepath, '**', fmt), recursive=True)
    else:
        return [x for x in filepath.split(',') if os.path.exists(x)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert GarmentCode spec to pattern.json")
    parser.add_argument("-f", "--files", default="design_yamls", type=str, help="Path to design files.") # The folder where the design data is stored
    parser.add_argument("-b", "--body", type=str, choices=['avg', 'thin', 'full-bodied', 'man','neutral'], default='neutral', help="Body to use.")
    parser.add_argument("-o", "--output", default='./Logs', type=str, help="Output file path.")
    parser.add_argument("-n", "--num_samples", default=-1, type=int, help="Number of samples to generate.")
    parser.add_argument('--fmt', default="*_params.yaml", type=str, help="Design file name format, used in glob.")

    args, cfg_cmd = parser.parse_known_args()

    body = BodyParameters(_BODY_MEASUREMENTS[args.body])
    design_files = _parse_file_path(args.files, args.fmt)
    print("Found %d design files: \n"%(len(design_files)), '\n'.join(design_files))

    if args.num_samples > 0 and len(design_files) > args.num_samples:
        # design_files = design_files[:args.num_samples]
        design_files = random.sample(design_files, args.num_samples)

    succeed_cnt = 0

    for design_file in tqdm(design_files):

        try:
            with open(design_file, 'rb') as f:
                design_data = yaml.safe_load(f)['design']

            piece = MetaGarment(os.path.basename(design_file).split('.')[0], body, design_data)
            pattern = piece.assembly()
            
            if piece.is_self_intersecting():
                print(f'{piece.name} is Self-intersecting')

            pattern_tag = '_' + datetime.now().strftime("%y%m%d-%H-%M-%S")
            folder = pattern.serialize(
                args.output,
                tag=pattern_tag,
                to_subfolder=True, 
                with_3d=False, with_text=False, view_ids=False)
            
            print(f"\n[SUCCEED] Saved to {folder}.")

            # # [OPTIONAL] copy original render views to the output folder
            # shutil.copyfile(
            #     design_file.replace('_design_params.yaml', '_render_front.png'), 
            #     os.path.join(folder, 'render_front.png'))
            # shutil.copyfile(
            #     design_file.replace('_design_params.yaml', '_render_back.png'), 
            #     os.path.join(folder, 'render_back.png'))
            
            # # [OPTIONAL] save body measurements
            # body.save(folder)

            # # [OPTIONAL] save design parameters
            # shutil.copy(design_file, folder)                      
                
        except Exception as e:
            print(f'[ERROR] {design_file}: {e}')

        succeed_cnt += 1

    print(f"Processing {len(design_files)} design files, {succeed_cnt} succeed.")