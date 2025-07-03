from torch.utils.data import DataLoader
import torch
from modelscope import AutoTokenizer
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor
import json
from lmm_utils.fintuned_qwen2vl_model import LoRAWithMLP
from lmm_utils.projector import vec_2_pattern_yaml
from lmm_utils.projector import save_design2yaml
import yaml
import os
import numpy as np
from lmm_utils.sim_utils import garmentyaml_folder2json_folder
from pathlib import Path
def load_system_config():
  root_path = Path(__file__).resolve().parent.parent # Navigate to the project's home directory
  config_path = root_path / "system.json"
  with open(config_path, "r") as f:
    return json.load(f)


_config = load_system_config()

class Predictor:
    def __init__(self, model_path="./lmm_utils/Qwen/Qwen2-VL-2B-Instruct", device=None,model_init=True):
        self.model_init = model_init
        if not model_init:
            return

        if device is None:
            self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        self.model =LoRAWithMLP(base_model_name=model_path, mlp_hidden_size=512, num_mlp_layers=2,
                            device=device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False, trust_remote_code=True)
        self.processor = AutoProcessor.from_pretrained(model_path)
        mask_list = torch.tensor([1, 1, 1, 1, 0, 0,
                                  1,  # fitted
                                  0, 0, 0,  # shirt
                                  1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0,   # collar b_beizer_y
                                  1, 1, 1, 0, 1, 0, 0,  # collar
                                  1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0,  # sleeve
                                  1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1,
                                  1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                                  1, 0, 0, 0, 0, 0,  # lfet sleeve _cuff
                                  0, 0, 0, 0, 0,  # skirt
                                  0, 0, 0, 0, 0, 0, 1, 0, 0, 0,  # flare-skirt
                                  1, 0, 0, 1, 0,  # godet-skirt
                                  0, 0, 0, 0, 0, 0, 0, 0, 1,  # peicl-skirt
                                  1, 1, 1, 0, 0, 0, 0,
                                  0, 0, 0, 0, 1, 0, 0, 0, 0, 0]).to(device=self.device)  # 1 represents the discrete value identified by the MMUA as the final result.
        self.mask_list = 1 - mask_list
        checkpoint = torch.load(
            _config['param_model'],
            map_location='cpu')
        self.model.load_state_dict(checkpoint['model_state_dict'], strict=False)  # Load the model parameters
        self.model.to(self.device)
    def predict(self,img_path,caption):
        messages_list = [[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": f"{img_path}",
                        "resized_height": 280,
                        "resized_width": 280,
                    },
                    {"type": "text", "text": f"garmentcode Yes:{caption}"},
                ],
            }
        ]]

        """
        The dataset is preprocessed
        """
        MAX_LENGTH = 8192
        input_ids, attention_mask, labels = [], [], []
        msgs = messages_list
        texts = self.processor.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
        # def process_func(self, conversation):
        image_inputs, video_inputs = process_vision_info(msgs)  # Get data (preprocessed)
        inputs = self.processor(
            text=texts,
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",

        )
        inputs['image_grid_thw'] = inputs['image_grid_thw']  # Transform from (1,h,w,c) to (h,w,c)
        input_ids = inputs['input_ids']
        attention_mask = inputs['attention_mask']
        labels = None
        batch = {"input_ids": input_ids, "attention_mask": attention_mask, "labels": labels,
                 "pixel_values": inputs['pixel_values'], "image_grid_thw": inputs['image_grid_thw']}
        batch = {k: v.to(self.device) for k, v in batch.items() if isinstance(v, torch.Tensor)}
        with torch.no_grad():
            outputs = self.model(**batch)
        outputs = outputs * self.mask_list
        return outputs

    def caption2yaml(self,caption, yaml_path='assets/design_params/default_text_value.yaml', new_yaml_path=None,
                     return_template_yaml='assets/design_params/default_template.yaml',
                     body_param_files="assets/bodies/mean_all_full.yaml", modify=False, image_path=None,
                     cache_input_design_data=None):
        '''Map the caption to a yaml file.
        Args：
            caption(list): the list generated by the large model.
            yaml_path (string): The basic YAML file used to fill in the value represented by the caption into the YAML file,
             which is a specially marked YAML file.
            new_yaml_path (string): Save this yaml file to a new path
            modify=False and text_bool=False, which are used to control the processing of the length of the lower body.
        Return ：
            design(dict): the data of the processed YAML file
        '''

        with open(body_param_files, 'r', encoding='utf-8') as yaml_file:
            body_param = yaml.safe_load(yaml_file)
            body = body_param['body']
        with open(yaml_path, 'r', encoding='utf-8') as yaml_file:
            default_yaml = yaml.safe_load(yaml_file)
            design = default_yaml['design']
        with open(return_template_yaml, 'r', encoding='utf-8') as yaml_file:
            default_template_yaml = yaml.safe_load(yaml_file)
            design_template = default_template_yaml['design']
        if cache_input_design_data is not None:
            design_template = cache_input_design_data

        for design_item in caption:
            design_item_list = design_item.split('__')
            temp = design
            template = design_template
            for i in range(len(design_item_list)):

                if i == (len(design_item_list) - 1):
                    final_text = design_item_list[i]
                    if final_text.isdigit():
                        final_text = int(final_text)
                    if final_text == 'None':
                        final_text = None
                    if final_text == 'True':
                        final_text = True
                    if final_text == 'False':
                        final_text = False
                    if isinstance(temp['range'][0], dict):
                        for item in temp['range']:
                            if final_text in item:
                                final_text = item[final_text]

                    temp['v'] = final_text
                    template['v'] = final_text
                else:
                    try:
                        temp = temp[design_item_list[i]]
                        template = template[design_item_list[i]]
                    except Exception as e:
                        print(temp)

        design = design_template
        if 'meta__upper__None' in caption:
            design['skirt']['rise']['v'] = 0.5
            design['flare-skirt']['rise']['v'] = 0.5
            design['pencil-skirt']['rise']['v'] = 0.5
            design['levels-skirt']['rise']['v'] = 0.5

            if "meta__bottom__SkirtManyPanels" in caption:
                if "flare-skirt__length__micro" in caption:
                    design['flare-skirt']['length']['v'] = 0.15
                if "flare-skirt__length__mini" in caption:
                    design['flare-skirt']['length']['v'] = 0.2
                if "flare-skirt__length__above-knee" in caption:
                    design['flare-skirt']['length']['v'] = 0.3

                if "flare-skirt__length__knee-length" in caption:
                    design['flare-skirt']['length']['v'] = 0.35
                if "flare-skirt__length__midi" in caption:
                    design['flare-skirt']['length']['v'] = 0.45
                if "flare-skirt__length__floor-length" in caption:
                    design['flare-skirt']['length']['v'] = 0.6

        if not modify:
            shirt_length = 0
            waist_length = 0
            if 'meta__upper__Shirt' in caption:
                front_frac = (body['bust'] - body['back_width']) / 2 / body['bust']
                fb_diff = (front_frac - (0.5 - front_frac)) * body['bust']
                sh_tan = float(np.tan(np.deg2rad(body['_shoulder_incl'])))
                shirt_length = design['shirt']['length']['v'] * body['waist_line'] - sh_tan * fb_diff

            if 'meta__upper__FittedShirt' in caption:
                m_bust = body['bust']
                front_frac = (body['bust'] - body['back_width']) / 2 / body['bust']
                sh_tan = float(np.tan(np.deg2rad(body['_shoulder_incl'])))
                width = front_frac * m_bust
                adjustment = sh_tan * (width - body['shoulder_w'] / 2)
                fitted_shirt_length = body['waist_over_bust_line'] - adjustment
                shirt_length = fitted_shirt_length

            if "meta__wb__None" not in caption:
                waist_length = design['waistband']['width']['v'] * body["hips_line"]
            if ("meta__bottom__None" not in caption and 'meta__bottom__Pants' not in caption
                    and 'meta__upper__None' not in caption and "meta__connected__True" in caption):
                if "meta__bottom__Skirt2" in caption:
                    if "skirt__length__micro" in caption:
                        all_length = 63.99739360159472
                        design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                          - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                         body["_leg_length"]
                    elif "skirt__length__mini" in caption:
                        all_length = 70.38289360159473
                        design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                          - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                         body["_leg_length"]

                    elif "skirt__length__above-knee" in caption:
                        all_length = 83.15389360159473
                        design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                          - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                         body["_leg_length"]

                    elif "skirt__length__knee-length" in caption:
                        all_length = 98.05339360159472
                        design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                          - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                         body["_leg_length"]

                    elif "skirt__length__midi" in caption:
                        all_length = 108.69589360159473
                        design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                          - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                         body["_leg_length"]

                    elif "skirt__length__floor-length" in caption:
                        all_length = 121.46689360159472
                        design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                          - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                         body["_leg_length"]

                elif ("meta__bottom__SkirtCircle" in caption or "meta__bottom__SkirtManyPanels" in caption
                      or "meta__bottom__AsymmSkirtCircle" in caption):
                    if "flare-skirt__length__micro" in caption:
                        all_length = 63.99739360159472
                        design['flare-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                - design['flare-skirt']['rise']['v'] * body[
                                                                    "hips_line"]) / \
                                                               body["_leg_length"]

                    elif "flare-skirt__length__mini" in caption:
                        all_length = 70.38289360159473
                        design['flare-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                - design['flare-skirt']['rise']['v'] * body[
                                                                    "hips_line"]) / \
                                                               body["_leg_length"]

                    elif "flare-skirt__length__above-knee" in caption:
                        all_length = 83.15389360159473
                        design['flare-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                - design['flare-skirt']['rise']['v'] * body[
                                                                    "hips_line"]) / \
                                                               body["_leg_length"]

                    elif "flare-skirt__length__knee-length" in caption:
                        all_length = 98.05339360159472
                        design['flare-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                - design['flare-skirt']['rise']['v'] * body[
                                                                    "hips_line"]) / \
                                                               body["_leg_length"]

                    elif "flare-skirt__length__midi" in caption:
                        all_length = 108.69589360159473
                        design['flare-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                - design['flare-skirt']['rise']['v'] * body[
                                                                    "hips_line"]) / \
                                                               body["_leg_length"]

                    elif "flare-skirt__length__floor-length" in caption:
                        all_length = 121.46689360159472
                        design['flare-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                - design['flare-skirt']['rise']['v'] * body[
                                                                    "hips_line"]) / \
                                                               body["_leg_length"]
                elif "meta__bottom__GodetSkirt" in caption:
                    if "godet-skirt__base__Skirt2" in caption:
                        if "skirt__length__micro" in caption:
                            all_length = 63.99739360159472
                            design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                              - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                             body["_leg_length"]

                        elif "skirt__length__mini" in caption:
                            all_length = 70.38289360159473
                            design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                              - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                             body["_leg_length"]

                        elif "skirt__length__above-knee" in caption:
                            all_length = 83.15389360159473
                            design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                              - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                             body["_leg_length"]

                        elif "skirt__length__knee-length" in caption:
                            all_length = 98.05339360159472
                            design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                              - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                             body["_leg_length"]

                        elif "skirt__length__midi" in caption:
                            all_length = 108.69589360159473
                            design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                              - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                             body["_leg_length"]

                        elif "skirt__length__floor-length" in caption:
                            all_length = 121.46689360159472
                            design['skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                              - design['skirt']['rise']['v'] * body["hips_line"]) / \
                                                             body["_leg_length"]

                    elif "godet-skirt__base__PencilSkirt" in caption:
                        if "pencil-skirt__length__micro" in caption:
                            all_length = 63.99739360159472
                            design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                     - design['pencil-skirt']['rise']['v'] * body[
                                                                         "hips_line"]) / \
                                                                    body["_leg_length"]

                        elif "pencil-skirt__length__mini" in caption:
                            all_length = 70.38289360159473
                            design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                     - design['pencil-skirt']['rise']['v'] * body[
                                                                         "hips_line"]) / \
                                                                    body["_leg_length"]

                        elif "pencil-skirt__length__above-knee" in caption:
                            all_length = 83.15389360159473
                            design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                     - design['pencil-skirt']['rise']['v'] * body[
                                                                         "hips_line"]) / \
                                                                    body["_leg_length"]

                        elif "pencil-skirt__length__knee-length" in caption:
                            all_length = 98.05339360159472
                            design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                     - design['pencil-skirt']['rise']['v'] * body[
                                                                         "hips_line"]) / \
                                                                    body["_leg_length"]

                        elif "pencil-skirt__length__midi" in caption:
                            all_length = 108.69589360159473
                            design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                     - design['pencil-skirt']['rise']['v'] * body[
                                                                         "hips_line"]) / \
                                                                    body["_leg_length"]

                        elif "pencil-skirt__length__floor-length" in caption:
                            all_length = 121.46689360159472
                            design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                     - design['pencil-skirt']['rise']['v'] * body[
                                                                         "hips_line"]) / \
                                                                    body["_leg_length"]

                elif "meta__bottom__PencilSkirt" in caption:

                    if "pencil-skirt__length__micro" in caption:
                        all_length = 63.99739360159472
                        design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['pencil-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "pencil-skirt__length__mini" in caption:
                        all_length = 70.38289360159473
                        design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['pencil-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]


                    elif "pencil-skirt__length__above-knee" in caption:
                        all_length = 83.15389360159473
                        design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length -
                                                                 design['pencil-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "pencil-skirt__length__knee-length" in caption:
                        all_length = 98.05339360159472
                        design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length -
                                                                 design['pencil-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "pencil-skirt__length__midi" in caption:
                        all_length = 108.69589360159473
                        design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length -
                                                                 design['pencil-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "pencil-skirt__length__floor-length" in caption:
                        all_length = 121.46689360159472
                        design['pencil-skirt']['length']['v'] = (all_length - shirt_length - waist_length -
                                                                 design['pencil-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                elif "meta__bottom__SkirtLevels" in caption:
                    if "levels-skirt__length__micro" in caption:
                        all_length = 63.99739360159472
                        design['levels-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['levels-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "levels-skirt__length__mini" in caption:
                        all_length = 63.99739360159472
                        design['levels-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['levels-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "levels-skirt__length__above-knee" in caption:
                        all_length = 83.15389360159473
                        design['levels-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['levels-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "levels-skirt__length__knee-length" in caption:
                        all_length = 98.05339360159472
                        design['levels-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['levels-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "levels-skirt__length__midi" in caption:
                        all_length = 108.69589360159473
                        design['levels-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['levels-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

                    elif "levels-skirt__length__floor-length" in caption:
                        all_length = 121.46689360159472
                        design['levels-skirt']['length']['v'] = (all_length - shirt_length - waist_length
                                                                 - design['levels-skirt']['rise']['v'] * body[
                                                                     "hips_line"]) / \
                                                                body["_leg_length"]

        if image_path and os.path.exists(image_path) and self.model_init:
            temp_cwd = os.getcwd()
            image_path = temp_cwd + '/' + image_path
            param_vec = self.predict(img_path=image_path, caption=caption)
            param_vec = param_vec[0].float().cpu().numpy()
            design = vec_2_pattern_yaml(design, param_vec, self.mask_list.tolist())

        if new_yaml_path is not None: save_design2yaml(design, new_yaml_path)
        return design

    def caption_json(self,caption, id="root",picture_path=None,dsl_ga=None):
        os.makedirs(f"user_data/temp_user_folder_for{id}gpt", exist_ok=True)
        self.caption2yaml(
            caption=caption,
            new_yaml_path=f"user_data/temp_user_folder_for{id}gpt/now_{id}.yaml",
            yaml_path="assets/design_params/default_text_value.yaml",
            image_path=picture_path
        )
        # In this case, a folder with the same name as the yaml file will be generated
        # under the corresponding output folder based on the file name of the yaml file,
        # and a json file with the same name as the yaml file will be the final result.
        # Here the output will be the now_picture file in the now_picture folder
        garmentyaml_folder2json_folder(
            input_folder=f"user_data/temp_user_folder_for{id}gpt",
            output_folder=f"user_data/temp_user_folder_for{id}gpt",
        )
