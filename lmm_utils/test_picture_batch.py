import os
import json
import uuid
import shutil
import argparse
import tqdm
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from helper import category2yaml2json
from lmm_utils.predict_garmentcode_picture import Predictor


def search_picture_files(directory):
    """Search for all image files in the directory"""
    picture_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.png', '.jpeg', '.gif')):
                picture_files.append(os.path.join(root, file))
    return picture_files


def main(input_folder_path, output_folder_path,sim_bool=False):
    dsl_ga = Predictor()
    all_picture_files = search_picture_files(input_folder_path)
    input_output_list = []
    uuid_list = []
    for input_picture_path in all_picture_files:
        output_json_path = input_picture_path.replace(input_folder_path, output_folder_path)
        output_json_dir = os.path.dirname(output_json_path)
        json_file_name = os.path.splitext(os.path.basename(input_picture_path))[0]
        output_json_path = os.path.join(output_json_dir, json_file_name, json_file_name + '.json')
        input_output_list.append((input_picture_path, output_json_path))
    threadPool = ThreadPoolExecutor(max_workers=5, thread_name_prefix="img_thread")
    futures = []
    for i, (input_picture_path, output_json_path) in tqdm.tqdm(enumerate(input_output_list)):
        if os.path.exists(output_json_path):
            continue
        item_id = str(uuid.uuid4())
        uuid_list.append(item_id)
        task = partial(
            category2yaml2json,
            category='picture',
            category_data=input_picture_path,
            final_json_path=output_json_path,
            id=item_id,
            model='Qwen/Qwen2.5-VL-72B-Instruct',
            base_url='https://api-inference.modelscope.cn/v1/',
            api_key='108a28f0-de01-4c43-b189-6cad25d32990',
            dsl_ga=dsl_ga,
            sim_bool=sim_bool
        )
        future = threadPool.submit(task)
        futures.append((future, input_picture_path))
        print(i, input_picture_path, output_json_path)
    fail_picture_list = []
    for future, input_picture_path in futures:
        try:
            result = future.result()
            print(f"Task result: {result}")
        except Exception as e:
            fail_picture_list.append(input_picture_path)
            print(f"Task failed: {e}")

    # Clean up the temporary folder
    for _uuid in uuid_list:
        try:
            shutil.rmtree(f"user_data/temp_user_folder_for{_uuid}gpt")
        except Exception as e:
            print(f"Error when deleting temp folder: {e}")
            pass

    threadPool.shutdown(wait=True)

    # Save the list of failures
    fail_dir = f"user_data/fail_{os.path.basename(input_folder_path)}"
    os.makedirs(fail_dir, exist_ok=True)
    with open(os.path.join(fail_dir, "fail_picture_list.json"), "w") as file:
        json.dump(fail_picture_list, file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Image-to-GarmentCode generation script")
    parser.add_argument('--input', type=str, required=True, help='Input image folder path')
    parser.add_argument('--output', type=str, required=True, help='Output folder path')
    parser.add_argument('--sim', type=bool, default=False, help='Enable simulation mode (default: False)')
    args = parser.parse_args()
    main(args.input, args.output,args.sim)
