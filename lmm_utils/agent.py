
import copy
from lmm_utils.core import MMUA
from lmm_utils.projector import input_caption2random_default_cption
from lmm_utils.predict_garmentcode_picture import Predictor

class Agent():
    def __init__(self,api_key=None, base_url=None, model=None,text_model=None,model_init=True):

        self.mmua=MMUA(api_key=api_key, base_url=base_url, model=model,text_model=text_model)
        self.dsl_ga= Predictor(model_init=model_init)

    def modify_design(self, design_list, text_prompt,design_params):
        
        gpt_design_list=None
        gpt_response=None
        gpt_design_params=None
        try:
            gpt_design_list, gpt_response = self.mmua.text_forusermodel_gpt(design_list,
                                                                            user_input=text_prompt)
        except Exception as e:
            print("modify_fail,trying again.please wait")
            try:
                gpt_design_list, gpt_response = self.mmua.text_forusermodel_gpt(design_list,
                                                                                user_input=text_prompt)
            except Exception as e:
                print("modify_fail,pleae input prompt again")
                gpt_response = "modify_fail,pleae input prompt again"
        if gpt_design_list is not None:
            gpt_design_list = input_caption2random_default_cption(gpt_design_list)
            more_caption_list = set(gpt_design_list)-set(design_list)
            gpt_design_params = self.dsl_ga.caption2yaml(more_caption_list,modify=True,cache_input_design_data=copy.deepcopy(design_params))
        return gpt_response, gpt_design_params, gpt_design_list


    def stress_design(self, design_list, img_url,design_params):
        gpt_design_list=None
        gpt_response=None
        gpt_design_params=None
        try:
            gpt_design_list, gpt_response = self.mmua.picture_caption_gpt_red(img_url, caption=design_list)
        except Exception as e:
            print("stress_fail,trying again.please wait")
            try:
                gpt_design_list, gpt_response = self.mmua.picture_caption_gpt_red(img_url, caption=design_list)
            except Exception as e:
                print("stress_fail,please input prompt and picture again")
                gpt_response = "stress_fail,please input prompt and picture again"
        if gpt_design_list is not None:
            gpt_design_list = input_caption2random_default_cption(gpt_design_list)
            more_caption_list = set(gpt_design_list) - set(design_list)
            gpt_design_params = self.dsl_ga.caption2yaml(more_caption_list, modify=True,
                                             cache_input_design_data=copy.deepcopy(design_params))
    
        return gpt_response, gpt_design_params, gpt_design_list


    def picture_text_design(self,  img_url,text_prompt):
        gpt_design_list=None
        gpt_response=None
        gpt_design_params=None
        recognize_picture_bool = True
        try:
            gpt_design_list, gpt_response = self.mmua.picture_gpt(img_url)
        except Exception as e:
            print(f"GPT_UTIL::Generation_FAILURE::Failed for image [I]{img_url} and [T]{text_prompt}"
                  f" due to {str(e)}, trying again...")
            try:
                gpt_design_list, gpt_response = self.mmua.picture_gpt(img_url)
            except Exception as e:
                print(f"GPT_UTIL::PARSE_FAILURE::Failed to parse image [I]{img_url} "
                      f"and [T]{text_prompt} again due to {str(e)}, give up.")
                gpt_response = "Generation failed, please try another image or prompt."
                recognize_picture_bool = False

        if recognize_picture_bool:
            try:
                gpt_design_list, gpt_response = self.mmua.text_forusermodel_gpt(
                    caption=gpt_design_list, user_input=text_prompt)
            except Exception as e:
                print(f"GPT_UTIL::AUTHORING_FAILURE::Failed to understand instruction {text_prompt} "
                      f"due to {str(e)}, trying again...")
                try:
                    gpt_design_list, gpt_response = self.mmua.text_forusermodel_gpt(
                        caption=gpt_design_list, user_input=text_prompt)
                except Exception as e:
                    print(f"GPT_UTIL::AUTHORING_FAILURE::Failed to understand instruction {text_prompt}"
                          f" due to {str(e)}, give up.")
                    gpt_response = "Authoring failed, please try another instruction."
        if gpt_design_list is not None:
            gpt_design_list = input_caption2random_default_cption(gpt_design_list)
            gpt_design_params = self.dsl_ga.caption2yaml(gpt_design_list)
        return gpt_response, gpt_design_params, gpt_design_list
    def picture_design(self, img_url):
        gpt_design_list=None
        gpt_response=None
        gpt_design_params=None
        try:
            gpt_design_list, gpt_response = self.mmua.picture_gpt(img_url)
        except Exception as e:
            print(f"GPT_UTIL::PARSE_IMAGE_FAILURE::Failed for image {img_url} due to {str(e)}, trying again...")
            try:
                gpt_design_list, gpt_response = self.mmua.picture_gpt(img_url)
            except Exception as e:
                print(f"GPT_UTIL::PARSE_IMAGE_FAILURE::Failed for image {img_url} due to {str(e)}, give up.")
                gpt_response = "Generation failed, please try another image."
        if gpt_design_list is not None:
            gpt_design_list = input_caption2random_default_cption(gpt_design_list)
            gpt_design_params = self.dsl_ga.caption2yaml(gpt_design_list,image_path=img_url)

        return gpt_response, gpt_design_params, gpt_design_list


    def text_design(self, text_prompt):
        gpt_design_list=None
        gpt_response=None
        gpt_design_params=None
        try:
            gpt_design_list, gpt_response = self.mmua.text_gpt(text_prompt)

        except Exception as e:
            print(f"GPT_UTIL::PARSE_TEXT_FAILURE::Failed to parse {text_prompt} due to {str(e)}, trying again...")
            try:
                gpt_design_list, gpt_response = self.mmua.text_gpt(text_prompt)
            except Exception as e:
                print(f"GPT_UTIL::PARSE_TEXT_FAILURE::Failed to parse {text_prompt} due to {str(e)}, give up.")
                gpt_response="Generation failed, please try another prompt."
        if gpt_design_list is not None:
            gpt_design_list = input_caption2random_default_cption(gpt_design_list)
            gpt_design_params = self.dsl_ga.caption2yaml(gpt_design_list)

        return gpt_response, gpt_design_params, gpt_design_list



