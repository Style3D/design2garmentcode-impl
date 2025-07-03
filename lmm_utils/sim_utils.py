import shutil
from pathlib import Path

import yaml

import pygarment.data_config as data_config
from assets.bodies.body_params import BodyParameters
from assets.garment_programs.meta_garment import MetaGarment
from pygarment.data_config import Properties
from pygarment.meshgen.boxmeshgen import BoxMesh
from pygarment.meshgen.sim_config import PathCofig
# from pygarment.meshgen.simulation import run_sim


#Convert the yaml file directly into an output plate
def garmentyaml_folder2json_folder(input_folder='', output_folder='',
                                   body_to_use='neutral'):
    ''' Convert the yaml files of the input folder to json files and save them in the output folder There is a folder with a yaml file name under the output folder, which contains JSON files and boilerplate images
    Args:
        input_folder(string): Enter a folder
        output_folder (string): The output folder
        body_to_use (string): Select a human body parameter
    '''

    bodies_measurements = {
        # Our model
        'neutral': './assets/bodies/mean_all.yaml',
        'mean_female': './assets/bodies/mean_female.yaml',
        'mean_male': './assets/bodies/mean_male.yaml',

        # SMPL
        'f_smpl': './assets/bodies/f_smpl_average_A40.yaml',
        'm_smpl': './assets/bodies/m_smpl_average_A40.yaml',
        #t pose
        'mean_all_tpose': './assets/bodies/mean_all_tpose.yaml'
    }
    body_to_use = body_to_use # CHANGE HERE to use different set of body measurements
    # body_to_use = 'mean_all_tpose'
    body = BodyParameters(bodies_measurements[body_to_use])

    design_files = {
        't-shirt': './assets/design_params/t-shirt.yaml',
        # Add paths HERE to load other parameters
    }

    pattern_dir = input_folder  # This is the input file, write the yaml folder here
    design_files_list = [file for file in Path(pattern_dir).iterdir() if file.suffix == '.yaml']

    design_files_stem = [item.stem for item in design_files_list]
    design_files_list = [str(item) for item in design_files_list]
    print(design_files_list)
    design_files = {
        k: v for k, v in zip(design_files_stem, design_files_list)

    }

    designs = {}
    for df in design_files:
        with open(design_files[df], 'r') as f:
            designs[df] = yaml.safe_load(f)['design']

    test_garments = []
    for df in designs:
        try:
            garment = MetaGarment(df, body, designs[df])
            test_garments.append(garment)
        except Exception as e:
            print(f"An error occurred with {df}: {e}")
            continue
    outpath = Path(output_folder)  # This is the folder for the output
    outpath.mkdir(parents=True, exist_ok=True)

    for piece in test_garments:
        pattern = piece.assembly()

        if piece.is_self_intersecting():
            print(f'{piece.name} is Self-intersecting')

        folder = pattern.serialize(
            outpath,
            tag='',
            to_subfolder=True,
            with_3d=False, with_text=False, view_ids=False,
            with_printable=True
        )

        body.save(folder)
        if piece.name in design_files:
            shutil.copy(design_files[piece.name], folder)
        else:
            shutil.copy(design_files['base'], folder)

        print(f'Success! {piece.name} saved to {folder}')


def json2modelfolder(input_json):
    ''' If you simulate a json file, you will save a folder in the directory where the json file is located, removing the specifiction ending as the folder name, and containing all the simulated information
    Args：
        input_json (string): A json file that needs to be mocked

    '''
    props = data_config.Properties('./assets/Sim_props/default_sim_props.yaml')
    props.set_section_stats('sim', fails={}, sim_time={}, spf={}, fin_frame={}, body_collisions={}, self_collisions={})
    props.set_section_stats('render', render_time={})

    input_path = Path(input_json)
    garment_name, _, _ = input_path.stem.rpartition('_')  # assuming ending in '_specification'
    # garment_name = os.path.splitext(os.path.basename(input_path))[0]
    sys_props = data_config.Properties('./system.json')
    paths = PathCofig(
        in_element_path=input_path.parent,
        out_path=input_path.parent,
        in_name=garment_name,
        body_name='mean_all',  # 'f_smpl_average_A40'
        smpl_body=False,  # NOTE: depends on chosen body model
        add_timestamp=False
    )

    # Generate and save garment box mesh (if not existent)
    print(f"Generate box mesh of {garment_name} with resolution {props['sim']['config']['resolution_scale']}...")
    print('\nGarment load: ', paths.in_g_spec)

    garment_box_mesh = BoxMesh(paths.in_g_spec, props['sim']['config']['resolution_scale'])
    garment_box_mesh.load()
    garment_box_mesh.serialize(
        paths, store_panels=False, uv_config=props['render']['config']['uv_texture'])

    props.serialize(paths.element_sim_props)

    run_sim(
        garment_box_mesh.name,
        props,
        paths,
        save_v_norms=False,
        store_usd=False,  # NOTE: False for fast simulation!
        optimize_storage=False,  # props['sim']['config']['optimize_storage'],
        verbose=False
    )

    props.serialize(paths.element_sim_props)


def modelandreturn_picture_path(input_json):

    ''' If you simulate a json file, you will save a folder in the directory where the json file is located, removing the specifiction ending as the folder name.
    Contains all the information for the simulation and returns the path to the simulation from the front perspective
    Args:
        input_json (string): A json file that needs to be mocked
    Responds:
        image_path2 (string): the path of the simulation map in the front view.

    '''

    json2modelfolder(input_json)
    input_json=Path(input_json)
    input_folder=input_json.parent
    garment_name, _, _ = input_json.stem.rpartition('_')
    image_path2=input_folder / garment_name / f"{str(garment_name)}_render_front.png"

    return image_path2
