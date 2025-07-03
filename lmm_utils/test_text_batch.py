import os
import shutil
import traceback
import json
import uuid
import argparse
from functools import partial
from concurrent.futures import ThreadPoolExecutor

from helper import category2yaml2json
from lmm_utils.predict_garmentcode_picture import Predictor
import tqdm


def main(input_text_json_path, output_folder_path,sim_bool=False):
    # Load the entered JSON text list
    with open(input_text_json_path, 'r') as f:
        all_text = json.load(f)

    input_output_list = []
    json_file_name = os.path.splitext(os.path.basename(input_text_json_path))[0]

    for index, input_text in enumerate(all_text):
        output_json_path = os.path.join(output_folder_path, json_file_name, str(index), f"{index}.json")
        input_output_list.append((input_text, output_json_path))

    # Initialize the predictor and thread pool
    dsl_ga = Predictor()
    threadPool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="test_")
    futures = []
    uuid_list = []

    for i, (input_text, output_json_path) in tqdm.tqdm(enumerate(input_output_list)):
        if os.path.exists(output_json_path):
            continue
        item_id = str(uuid.uuid4())
        uuid_list.append(item_id)

        task = partial(
            category2yaml2json,
            category='text',
            category_data=input_text,
            final_json_path=output_json_path,
            id=item_id,
            model='Qwen/Qwen2.5-72B-Instruct',
            base_url='https://api-inference.modelscope.cn/v1/',
            api_key='108a28f0-de01-4c43-b189-6cad25d32990',
            dsl_ga=dsl_ga,
            sim_bool=sim_bool
        )
        future = threadPool.submit(task)
        futures.append((future, input_text))
        print(i, input_text, output_json_path)

    # Collect failure information
    fail_picture_list = []
    for future, input_text in futures:
        try:
            result = future.result()
            print(f"Task result: {result}")
        except Exception as e:
            traceback.print_exc()
            fail_picture_list.append(input_text)
            print(f"Task failed: {e}")

    # Clean up the temporary folder
    for _uuid in uuid_list:
        try:
            shutil.rmtree(f"user_data/temp_user_folder_for{_uuid}gpt")
        except Exception as e:
            print(f"Error when deleting temp folder: {e}")
            pass

    threadPool.shutdown(wait=True)

    # Save a record of failures
    fail_dir = f"user_data/fail_{os.path.basename(input_text_json_path).split('.')[0]}"
    os.makedirs(fail_dir, exist_ok=True)
    with open(os.path.join(fail_dir, "fail_picture_list.json"), "w") as file:
        json.dump(fail_picture_list, file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text-to-GarmentCode generation script")
    parser.add_argument('--input', type=str, required=True, help='Path to input JSON file with text list')
    parser.add_argument('--output', type=str, required=True, help='Path to output folder for results')
    parser.add_argument('--sim', type=bool, default=False, help='Enable simulation mode (default: False)')
    args = parser.parse_args()
    main(args.input, args.output,args.sim)
