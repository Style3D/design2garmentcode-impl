import os
from lmm_utils.core import MMUA
import shutil
from lmm_utils.projector import  input_caption2random_default_cption
import json
import time
from sim_utils import modelandreturn_picture_path, garmentyaml_folder2json_folder
from lmm_utils.predict_garmentcode_picture import Predictor


def category2yaml2json(
    category,
    category_data,
    final_json_path=None,
    sim_bool=False,
    id="root",
    api_key=None,
    base_url=None,
    model=None,
    dsl_ga=None,
):
    """Specify the different types of data, pass in the data, and get a json file to generate the result for the final boilerplate.
    Args:
        category(string): Specify the type of input 'picture' 'text' 'list'
        category_data: List or ImagePath(String) or Text(String) Enter different specific data depending on the type
        final_json_path (string): specifies the final JSON path,
        At the same time, the json file of the template data, the template image, the converted stylexd format, and the template generation time will be generated in the json folder
        sim_bool (bool): Specifies whether simulation is required
        id(string): Create a folder under the user_data based on the ID you entered temp_user_folder_for{id}gpt contains all the data related to the template generated this time.
        api_key (string): Specifies the API to access the model, if the input is None, the default API will be called
        base_url (string): Specifies the URL to be visited, if the input is None, the default API will be called
        model(string): Specifies the model to be accessed, if the input is None, the default model will be called
    Return ：
        json_list (list): the list selected by the large model
        response(string): the reply of the large model, removing the list content in the reply
    """

    mmua_llm = MMUA(api_key=api_key, base_url=base_url, model=model)
    if dsl_ga is None:
        dsl_ga = Predictor()
    gpt_respond = None
    start_time = time.time()
    json_list = []
    picture_path = None
    if category == "picture":  # The corresponding category_data is the image path
        json_list, gpt_respond = mmua_llm.picture_gpt(category_data)
        picture_path = category_data
    if category == "text":  # The text corresponding to the input
        json_list, gpt_respond = mmua_llm.text_gpt(category_data)
    if category == "list":  # It's the list of captions
        json_list = category_data
    caption_json_list = json_list
    json_list = input_caption2random_default_cption(json_list)
    dsl_ga.caption_json(caption=json_list, id=id,picture_path=picture_path)
    end_time = time.time()

    pattern_generate_time = end_time - start_time
    print(pattern_generate_time)

    temp_json_file_path = (
        f"user_data/temp_user_folder_for{id}gpt/now_{id}/now_{id}_specification.json"
    )
    if final_json_path is not None:
        final_json_dirname = os.path.dirname(final_json_path)
        os.makedirs(final_json_dirname, exist_ok=True)

        with open(f"{final_json_dirname}/pattern_generate_time.txt", "a") as f:
            f.write(f"pattern_generate_time：{pattern_generate_time:.4f} s\n")

        with open(f"{final_json_dirname}/caption.json", "w") as file:
            json.dump(caption_json_list, file, indent=4)

        with open(f"{final_json_dirname}/gpt_respond.txt", "w") as file:
            file.write(gpt_respond)
        f"user_data/temp_user_folder_for{id}gpt"
        # Define the source file path

        print("temp_json_file_path", temp_json_file_path)
        # print("temp_json_file_path",temp_json_file_path)

        # Define the target file path, including the new file name
        destination = final_json_path

        # Copy the file and retain the metadata, while modifying the file name
        shutil.copy2(temp_json_file_path, destination)
        if category == "text":
            with open(f"{final_json_dirname}/user_input.txt", "w") as file:
                # Write text
                file.write(category_data)
        if category == "picture":
            image_path = category_data
            # Next, save the original image to the folder where the json path is located, and name it the same as this json file, but with a different extension
            _, picture_file_extension = os.path.splitext(image_path)
            picture_file_path, _ = os.path.splitext(final_json_path)
            # Composite the new image path, here the name of the image is changed
            picture_path = picture_file_path + picture_file_extension
            shutil.copy2(image_path, picture_path)

        filename = os.path.splitext(os.path.basename(final_json_path))[0]

        if category == "list": pass
        if sim_bool:
            modelandreturn_picture_path(temp_json_file_path)
            model_png = f"user_data/temp_user_folder_for{id}gpt/now_{id}/now_{id}/now_{id}_render_front.png"
            #Copy the mockup to the destination folder
            model_png_end_path = final_json_dirname + "/sim_garment_front.png"
            shutil.copy2(model_png, model_png_end_path)
            model_png = f"user_data/temp_user_folder_for{id}gpt/now_{id}/now_{id}/now_{id}_render_back.png"
            # Copy the mockup to the destination folder
            model_png_end_path = final_json_dirname + "/sim_garment_back.png"

            shutil.copy2(model_png, model_png_end_path)

        # Duplicate the PNG image of the plate

        pattern_png = (
            f"user_data/temp_user_folder_for{id}gpt/now_{id}/now_{id}_pattern.png"
        )
        pattern_png_end_path = final_json_dirname + f"/{filename}_pattern.png"
        shutil.copy2(pattern_png, pattern_png_end_path)

        # Copy the yaml file
        yaml_file = f"user_data/temp_user_folder_for{id}gpt//now_{id}/now_{id}.yaml"
        yaml_end_path = final_json_dirname + f"/{filename}.yaml"
        shutil.copy2(yaml_file, yaml_end_path)
    if final_json_path is None:
        temp_json_dirname = os.path.dirname(temp_json_file_path)
        with open(f"{temp_json_dirname}/pattern_generate_time.txt", "a") as f:
            f.write(f"pattern_generate_time：{pattern_generate_time:.4f} s\n")

        with open(f"{temp_json_dirname}/caption.json", "w") as file:
            json.dump(caption_json_list, file, indent=4)

        with open(f"{temp_json_dirname}/gpt_respond.txt", "w") as file:
            file.write(gpt_respond)

        if category == "text":
            with open(f"{temp_json_dirname}/user_input.txt", "w") as file:
                # Write text
                file.write(category_data)
        if category == "picture":
            image_path = category_data
            # Next, save the original image to the folder where the json path is located, and name it the same as this json file, but with a different extension
            _, picture_file_extension = os.path.splitext(image_path)
            picture_file_path, _ = os.path.splitext(temp_json_file_path)
            # Composite the new image path, here the name of the image is changed
            picture_path = picture_file_path + picture_file_extension

            shutil.copy2(image_path, picture_path)
        if sim_bool:
            modelandreturn_picture_path(temp_json_file_path)

    return json_list, gpt_respond
