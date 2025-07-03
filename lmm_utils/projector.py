import os
import uuid
import json
import yaml
import random
import numpy as np
from collections import OrderedDict

# from predict_garmentcode_picture import predict
CONNECT_TAG = '__'

all_text_dict={
  "meta__upper": [
    "meta__upper__FittedShirt",
    "meta__upper__Shirt",
    "meta__upper__None"
  ],
  "meta__wb": [
    "meta__wb__StraightWB",
    "meta__wb__FittedWB",
    "meta__wb__None"
  ],
  "meta__bottom": [
    "meta__bottom__SkirtCircle",
    "meta__bottom__AsymmSkirtCircle",
    "meta__bottom__GodetSkirt",
    "meta__bottom__Pants",
    "meta__bottom__Skirt2",
    "meta__bottom__SkirtManyPanels",
    "meta__bottom__PencilSkirt",
    "meta__bottom__SkirtLevels",
    "meta__bottom__None"
  ],
  "meta__connected": [
    "meta__connected__True",
    "meta__connected__False"
  ],
  "waistband__waist": [
    "waistband__waist__fitted",
    "waistband__waist__slightly-loose",
    "waistband__waist__loose"
  ],
  "waistband__width": [
    "waistband__width__narrow",
    "waistband__width__medium",
    "waistband__width__wide"
  ],
  "fitted_shirt__strapless": [
    "fitted_shirt__strapless__True",
    "fitted_shirt__strapless__False"
  ],
  "shirt__length": [
    "shirt__length__super-cropped",
    "shirt__length__regular",
    "shirt__length__long"
  ],
  "shirt__width": [
    "shirt__width__normal",
    "shirt__width__relaxed"
  ],
  "shirt__flare": [
    "shirt__flare__tight",
    "shirt__flare__straight",
    "shirt__flare__flared",
    "shirt__flare__very-flared"
  ],
  "collar__f_collar": [
    "collar__f_collar__CircleNeckHalf",
    "collar__f_collar__CurvyNeckHalf",
    "collar__f_collar__VNeckHalf",
    "collar__f_collar__SquareNeckHalf",
    "collar__f_collar__TrapezoidNeckHalf",
    "collar__f_collar__CircleArcNeckHalf",
    "collar__f_collar__Bezier2NeckHalf"
  ],
  "collar__b_collar": [
    "collar__b_collar__CircleNeckHalf",
    "collar__b_collar__CurvyNeckHalf",
    "collar__b_collar__VNeckHalf",
    "collar__b_collar__SquareNeckHalf",
    "collar__b_collar__TrapezoidNeckHalf",
    "collar__b_collar__CircleArcNeckHalf",
    "collar__b_collar__Bezier2NeckHalf"
  ],
  "collar__width": [
    "collar__width__very-narrow",
    "collar__width__medium",
    "collar__width__wide"
  ],
  "collar__fc_depth": [
    "collar__fc_depth__shallow",
    "collar__fc_depth__medium",
    "collar__fc_depth__deep"
  ],
  "collar__bc_depth": [
    "collar__bc_depth__shallow",
    "collar__bc_depth__medium",
    "collar__bc_depth__deep"
  ],
  "collar__fc_angle": [
    "collar__fc_angle__acute",
    "collar__fc_angle__standard",
    "collar__fc_angle__obtuse"
  ],
  "collar__bc_angle": [
    "collar__bc_angle__acute",
    "collar__bc_angle__standard",
    "collar__bc_angle__obtuse"
  ],
  "collar__f_bezier_x": [
    "collar__f_bezier_x__left",
    "collar__f_bezier_x__center",
    "collar__f_bezier_x__right"
  ],
  "collar__f_bezier_y": [
    "collar__f_bezier_y__top",
    "collar__f_bezier_y__center",
    "collar__f_bezier_y__bottom"
  ],
  "collar__b_bezier_x": [
    "collar__b_bezier_x__left",
    "collar__b_bezier_x__center",
    "collar__b_bezier_x__right"
  ],
  "collar__b_bezier_y": [
    "collar__b_bezier_y__top",
    "collar__b_bezier_y__center",
    "collar__b_bezier_y__bottom"
  ],
  "collar__f_flip_curve": [
    "collar__f_flip_curve__True",
    "collar__f_flip_curve__False"
  ],
  "collar__b_flip_curve": [
    "collar__b_flip_curve__True",
    "collar__b_flip_curve__False"
  ],
  "collar__component__style": [
    "collar__component__style__Turtle",
    "collar__component__style__SimpleLapel",
    "collar__component__style__Hood2Panels",
    "collar__component__style__None"
  ],
  "collar__component__depth": [
    "collar__component__depth__shallow",
    "collar__component__depth__medium",
    "collar__component__depth__deep"
  ],
  "collar__component__lapel_standing": [
    "collar__component__lapel_standing__True",
    "collar__component__lapel_standing__False"
  ],
  "collar__component__hood_depth": [
    "collar__component__hood_depth__shallow",
    "collar__component__hood_depth__medium",
    "collar__component__hood_depth__deep"
  ],
  "collar__component__hood_length": [
    "collar__component__hood_length__short",
    "collar__component__hood_length__medium",
    "collar__component__hood_length__long"
  ],
  "sleeve__sleeveless": [
    "sleeve__sleeveless__True",
    "sleeve__sleeveless__False"
  ],
  "sleeve__armhole_shape": [
    "sleeve__armhole_shape__ArmholeSquare",
    "sleeve__armhole_shape__ArmholeAngle",
    "sleeve__armhole_shape__ArmholeCurve"
  ],
  "sleeve__length": [
    "sleeve__length__short",
    "sleeve__length__half",
    "sleeve__length__three-quarter",
    "sleeve__length__long",
    "sleeve__length__full"
  ],
  "sleeve__connecting_width": [
    "sleeve__connecting_width__narrow",
    "sleeve__connecting_width__medium",
    "sleeve__connecting_width__loose",
    "sleeve__connecting_width__very-loose"
  ],
  "sleeve__end_width": [
    "sleeve__end_width__closing",
    "sleeve__end_width__straight",
    "sleeve__end_width__opening"
  ],
  "sleeve__sleeve_angle": [
    "sleeve__sleeve_angle__small",
    "sleeve__sleeve_angle__medium",
    "sleeve__sleeve_angle__large"
  ],
  "sleeve__opening_dir_mix": [
    "sleeve__opening_dir_mix__negative-twist",
    "sleeve__opening_dir_mix__standard",
    "sleeve__opening_dir_mix__positive-twist"
  ],
  "sleeve__standing_shoulder": [
    "sleeve__standing_shoulder__True",
    "sleeve__standing_shoulder__False"
  ],
  "sleeve__standing_shoulder_len": [
    "sleeve__standing_shoulder_len__short",
    "sleeve__standing_shoulder_len__medium",
    "sleeve__standing_shoulder_len__long"
  ],
  "sleeve__connect_ruffle": [
    "sleeve__connect_ruffle__none",
    "sleeve__connect_ruffle__some",
    "sleeve__connect_ruffle__obvious"
  ],
  "sleeve__smoothing_coeff": [
    "sleeve__smoothing_coeff__very-smooth",
    "sleeve__smoothing_coeff__moderate",
    "sleeve__smoothing_coeff__less-smooth"
  ],
  "sleeve__cuff__type": [
    "sleeve__cuff__type__CuffBand",
    "sleeve__cuff__type__CuffSkirt",
    "sleeve__cuff__type__CuffBandSkirt",
    "sleeve__cuff__type__None"
  ],
  "sleeve__cuff__top_ruffle": [
    "sleeve__cuff__top_ruffle__straight",
    "sleeve__cuff__top_ruffle__tapered",
    "sleeve__cuff__top_ruffle__very_tapered"
  ],
  "sleeve__cuff__cuff_len": [
    "sleeve__cuff__cuff_len__short",
    "sleeve__cuff__cuff_len__medium",
    "sleeve__cuff__cuff_len__long"
  ],
  "sleeve__cuff__skirt_fraction": [
    "sleeve__cuff__skirt_fraction__small",
    "sleeve__cuff__skirt_fraction__medium",
    "sleeve__cuff__skirt_fraction__large"
  ],
  "sleeve__cuff__skirt_flare": [
    "sleeve__cuff__skirt_flare__slight",
    "sleeve__cuff__skirt_flare__moderate",
    "sleeve__cuff__skirt_flare__significant"
  ],
  "sleeve__cuff__skirt_ruffle": [
    "sleeve__cuff__skirt_ruffle__none",
    "sleeve__cuff__skirt_ruffle__some"
  ],
  "left__enable_asym": [
    "left__enable_asym__True",
    "left__enable_asym__False"
  ],
  "left__fitted_shirt__strapless": [
    "left__fitted_shirt__strapless__True",
    "left__fitted_shirt__strapless__False"
  ],
  "left__shirt__width": [
    "left__shirt__width__normal",
    "left__shirt__width__relaxed"
  ],
  "left__shirt__flare": [
    "left__shirt__flare__tight",
    "left__shirt__flare__straight",
    "left__shirt__flare__flared",
    "left__shirt__flare__very-flared"
  ],
  "left__collar__f_collar": [
    "left__collar__f_collar__CircleNeckHalf",
    "left__collar__f_collar__CurvyNeckHalf",
    "left__collar__f_collar__VNeckHalf",
    "left__collar__f_collar__SquareNeckHalf",
    "left__collar__f_collar__TrapezoidNeckHalf",
    "left__collar__f_collar__CircleArcNeckHalf",
    "left__collar__f_collar__Bezier2NeckHalf"
  ],
  "left__collar__b_collar": [
    "left__collar__b_collar__CircleNeckHalf",
    "left__collar__b_collar__CurvyNeckHalf",
    "left__collar__b_collar__VNeckHalf",
    "left__collar__b_collar__SquareNeckHalf",
    "left__collar__b_collar__TrapezoidNeckHalf",
    "left__collar__b_collar__CircleArcNeckHalf",
    "left__collar__b_collar__Bezier2NeckHalf"
  ],
  "left__collar__width": [
    "left__collar__width__narrow",
    "left__collar__width__medium",
    "left__collar__width__wide"
  ],
  "left__collar__fc_angle": [
    "left__collar__fc_angle__acute",
    "left__collar__fc_angle__standard",
    "left__collar__fc_angle__obtuse"
  ],
  "left__collar__bc_angle": [
    "left__collar__bc_angle__acute",
    "left__collar__bc_angle__standard",
    "left__collar__bc_angle__obtuse"
  ],
  "left__collar__f_bezier_x": [
    "left__collar__f_bezier_x__left",
    "left__collar__f_bezier_x__center",
    "left__collar__f_bezier_x__right"
  ],
  "left__collar__f_bezier_y": [
    "left__collar__f_bezier_y__top",
    "left__collar__f_bezier_y__center",
    "left__collar__f_bezier_y__bottom"
  ],
  "left__collar__b_bezier_x": [
    "left__collar__b_bezier_x__left",
    "left__collar__b_bezier_x__center",
    "left__collar__b_bezier_x__right"
  ],
  "left__collar__b_bezier_y": [
    "left__collar__b_bezier_y__top",
    "left__collar__b_bezier_y__center",
    "left__collar__b_bezier_y__bottom"
  ],
  "left__collar__f_flip_curve": [
    "left__collar__f_flip_curve__True",
    "left__collar__f_flip_curve__False"
  ],
  "left__collar__b_flip_curve": [
    "left__collar__b_flip_curve__True",
    "left__collar__b_flip_curve__False"
  ],
  "left__sleeve__sleeveless": [
    "left__sleeve__sleeveless__True",
    "left__sleeve__sleeveless__False"
  ],
  "left__sleeve__armhole_shape": [
    "left__sleeve__armhole_shape__ArmholeSquare",
    "left__sleeve__armhole_shape__ArmholeAngle",
    "left__sleeve__armhole_shape__ArmholeCurve"
  ],
  "left__sleeve__length": [
    "left__sleeve__length__short",
    "left__sleeve__length__half",
    "left__sleeve__length__three-quarter",
    "left__sleeve__length__long",
    "left__sleeve__length__full"
  ],
  "left__sleeve__connecting_width": [
    "left__sleeve__connecting_width__narrow",
    "left__sleeve__connecting_width__medium",
    "left__sleeve__connecting_width__loose",
    "left__sleeve__connecting_width__very-loose"
  ],
  "left__sleeve__end_width": [
    "left__sleeve__end_width__closing",
    "left__sleeve__end_width__straight",
    "left__sleeve__end_width__opening"
  ],
  "left__sleeve__sleeve_angle": [
    "left__sleeve__sleeve_angle__small",
    "left__sleeve__sleeve_angle__medium",
    "left__sleeve__sleeve_angle__large"
  ],
  "left__sleeve__opening_dir_mix": [
    "left__sleeve__opening_dir_mix__negative-twist",
    "left__sleeve__opening_dir_mix__standard",
    "left__sleeve__opening_dir_mix__positive-twist"
  ],
  "left__sleeve__standing_shoulder": [
    "left__sleeve__standing_shoulder__True",
    "left__sleeve__standing_shoulder__False"
  ],
  "left__sleeve__standing_shoulder_len": [
    "left__sleeve__standing_shoulder_len__short",
    "left__sleeve__standing_shoulder_len__medium",
    "left__sleeve__standing_shoulder_len__long"
  ],
  "left__sleeve__connect_ruffle": [
    "left__sleeve__connect_ruffle__none",
    "left__sleeve__connect_ruffle__some",
    "left__sleeve__connect_ruffle__obvious"
  ],
  "left__sleeve__smoothing_coeff": [
    "left__sleeve__smoothing_coeff__very-smooth",
    "left__sleeve__smoothing_coeff__moderate",
    "left__sleeve__smoothing_coeff__less-smooth"
  ],
  "left__sleeve__cuff__type": [
    "left__sleeve__cuff__type__CuffBand",
    "left__sleeve__cuff__type__CuffSkirt",
    "left__sleeve__cuff__type__CuffBandSkirt",
    "left__sleeve__cuff__type__None"
  ],
  "left__sleeve__cuff__top_ruffle": [
    "left__sleeve__cuff__top_ruffle__none",
    "left__sleeve__cuff__top_ruffle__moderate",
    "left__sleeve__cuff__top_ruffle__obvious"
  ],
  "left__sleeve__cuff__cuff_len": [
    "left__sleeve__cuff__cuff_len__short",
    "left__sleeve__cuff__cuff_len__medium",
    "left__sleeve__cuff__cuff_len__long"
  ],
  "left__sleeve__cuff__skirt_fraction": [
    "left__sleeve__cuff__skirt_fraction__small",
    "left__sleeve__cuff__skirt_fraction__medium",
    "left__sleeve__cuff__skirt_fraction__large"
  ],
  "left__sleeve__cuff__skirt_flare": [
    "left__sleeve__cuff__skirt_flare__slight",
    "left__sleeve__cuff__skirt_flare__moderate",
    "left__sleeve__cuff__skirt_flare__significant"
  ],
  "left__sleeve__cuff__skirt_ruffle": [
    "left__sleeve__cuff__skirt_ruffle__none",
    "left__sleeve__cuff__skirt_ruffle__some"
  ],
  "skirt__length": [
    "skirt__length__micro",
    "skirt__length__mini",
    "skirt__length__above-knee",
    "skirt__length__knee-length",
    "skirt__length__midi",
    "skirt__length__floor-length"
  ],
  "skirt__rise": [
    "skirt__rise__low",
    "skirt__rise__mid",
    "skirt__rise__high"
  ],
  "skirt__ruffle": [
    "skirt__ruffle__none",
    "skirt__ruffle__moderate",
    "skirt__ruffle__rich"
  ],
  "skirt__bottom_cut": [
    "skirt__bottom_cut__none",
    "skirt__bottom_cut__shallow",
    "skirt__bottom_cut__deep"
  ],
  "skirt__flare": [
    "skirt__flare__small",
    "skirt__flare__medium",
    "skirt__flare__large"
  ],
  "flare-skirt__length": [
    "flare-skirt__length__micro",
    "flare-skirt__length__mini",
    "flare-skirt__length__above-knee",
    "flare-skirt__length__knee-length",
    "flare-skirt__length__midi",
    "flare-skirt__length__floor-length"
  ],
  "flare-skirt__rise": [
    "flare-skirt__rise__low",
    "flare-skirt__rise__mid",
    "flare-skirt__rise__high"
  ],
  "flare-skirt__suns": [
    "flare-skirt__suns__slight",
    "flare-skirt__suns__moderate",
    "flare-skirt__suns__significant"
  ],
  "flare-skirt__skirt-many-panels__n_panels": [
    "flare-skirt__skirt-many-panels__n_panels__few",
    "flare-skirt__skirt-many-panels__n_panels__medium",
    "flare-skirt__skirt-many-panels__n_panels__many"
  ],
  "flare-skirt__skirt-many-panels__panel_curve": [
    "flare-skirt__skirt-many-panels__panel_curve__inward",
    "flare-skirt__skirt-many-panels__panel_curve__straight",
    "flare-skirt__skirt-many-panels__panel_curve__outward"
  ],
  "flare-skirt__asymm__front_length": [
    "flare-skirt__asymm__front_length__highly-asymmetric",
    "flare-skirt__asymm__front_length__strongly-asymmetric",
    "flare-skirt__asymm__front_length__moderately-asymmetric",
    "flare-skirt__asymm__front_length__slightly-asymmetric",
    "flare-skirt__asymm__front_length__symmetric"
  ],
  "flare-skirt__cut__add": [
    "flare-skirt__cut__add__True",
    "flare-skirt__cut__add__False"
  ],
  "flare-skirt__cut__depth": [
    "flare-skirt__cut__depth__shallow",
    "flare-skirt__cut__depth__medium",
    "flare-skirt__cut__depth__deep"
  ],
  "flare-skirt__cut__width": [
    "flare-skirt__cut__width__narrow",
    "flare-skirt__cut__width__medium",
    "flare-skirt__cut__width__wide"
  ],
  "flare-skirt__cut__place": [
    "flare-skirt__cut__place__back_left",
    "flare-skirt__cut__place__back_center",
    "flare-skirt__cut__place__back_right",
    "flare-skirt__cut__place__front_left",
    "flare-skirt__cut__place__front_center",
    "flare-skirt__cut__place__front_right",
  ],
  "godet-skirt__base": [
    "godet-skirt__base__Skirt2",
    "godet-skirt__base__PencilSkirt"
  ],
  "godet-skirt__insert_w": [
    "godet-skirt__insert_w__narrow",
    "godet-skirt__insert_w__medium",
    "godet-skirt__insert_w__wide"
  ],
  "godet-skirt__insert_depth": [
    "godet-skirt__insert_depth__shallow",
    "godet-skirt__insert_depth__medium",
    "godet-skirt__insert_depth__deep"
  ],
  "godet-skirt__num_inserts": [
    "godet-skirt__num_inserts__4",
    "godet-skirt__num_inserts__6",
    "godet-skirt__num_inserts__8",
    "godet-skirt__num_inserts__10",
    "godet-skirt__num_inserts__12"
  ],
  "godet-skirt__cuts_distance": [
    "godet-skirt__cuts_distance__close",
    "godet-skirt__cuts_distance__medium",
    "godet-skirt__cuts_distance__far"
  ],
  "pencil-skirt__length": [
    "pencil-skirt__length__micro",
    "pencil-skirt__length__mini",
    "pencil-skirt__length__above-knee",
    "pencil-skirt__length__knee-length",
    "pencil-skirt__length__midi",
    "pencil-skirt__length__floor-length"
  ],
  "pencil-skirt__rise": [
    "pencil-skirt__rise__low",
    "pencil-skirt__rise__mid",
    "pencil-skirt__rise__high"
  ],
  "pencil-skirt__flare": [
    "pencil-skirt__flare__tight",
    "pencil-skirt__flare__straight",
    "pencil-skirt__flare__slight-flare"
  ],
  "pencil-skirt__low_angle": [
    "pencil-skirt__low_angle__inward",
    "pencil-skirt__low_angle__straight",
    "pencil-skirt__low_angle__outward"
  ],
  "pencil-skirt__front_slit": [
    "pencil-skirt__front_slit__none",
    "pencil-skirt__front_slit__shallow",
    "pencil-skirt__front_slit__deep"
  ],
  "pencil-skirt__back_slit": [
    "pencil-skirt__back_slit__none",
    "pencil-skirt__back_slit__shallow",
    "pencil-skirt__back_slit__deep"
  ],
  "pencil-skirt__left_slit": [
    "pencil-skirt__left_slit__none",
    "pencil-skirt__left_slit__shallow",
    "pencil-skirt__left_slit__deep"
  ],
  "pencil-skirt__right_slit": [
    "pencil-skirt__right_slit__none",
    "pencil-skirt__right_slit__shallow",
    "pencil-skirt__right_slit__deep"
  ],
  "pencil-skirt__style_side_cut": [
    "pencil-skirt__style_side_cut__Sun",
    "pencil-skirt__style_side_cut__SIGGRAPH_logo",
    "pencil-skirt__style_side_cut__None"
  ],
  "levels-skirt__base": [
    "levels-skirt__base__Skirt2",
    "levels-skirt__base__PencilSkirt",
    "levels-skirt__base__SkirtCircle",
    "levels-skirt__base__AsymmSkirtCircle"
  ],
  "levels-skirt__level": [
    "levels-skirt__level__Skirt2",
    "levels-skirt__level__SkirtCircle",
    "levels-skirt__level__AsymmSkirtCircle"
  ],
  "levels-skirt__num_levels": [
    "levels-skirt__num_levels__1",
    "levels-skirt__num_levels__2",
    "levels-skirt__num_levels__3",
    "levels-skirt__num_levels__4",
    "levels-skirt__num_levels__5"
  ],
  "levels-skirt__level_ruffle": [
    "levels-skirt__level_ruffle__none",
    "levels-skirt__level_ruffle__moderate",
    "levels-skirt__level_ruffle__rich"
  ],
  "levels-skirt__length": [
    "levels-skirt__length__micro",
    "levels-skirt__length__mini",
    "levels-skirt__length__above-knee",
    "levels-skirt__length__knee-length",
    "levels-skirt__length__midi",
    "levels-skirt__length__floor-length"
  ],
  "levels-skirt__rise": [
    "levels-skirt__rise__low",
    "levels-skirt__rise__mid",
    "levels-skirt__rise__high"
  ],
  "levels-skirt__base_length_frac": [
    "levels-skirt__base_length_frac__short",
    "levels-skirt__base_length_frac__medium",
    "levels-skirt__base_length_frac__long"
  ],
  "pants__length": [
    "pants__length__micro",
    "pants__length__short",
    "pants__length__knee-length",
    "pants__length__capri",
    "pants__length__ankle-length",
    "pants__length__full-length"
  ],
  "pants__width": [
    "pants__width__fitted",
    "pants__width__normal",
    "pants__width__loose"
  ],
  "pants__flare": [
    "pants__flare__tapering",
    "pants__flare__straight",
    "pants__flare__slight-flare"
  ],
  "pants__rise": [
    "pants__rise__low",
    "pants__rise__mid",
    "pants__rise__high"
  ],
  "pants__cuff__type": [
    "pants__cuff__type__CuffBand",
    "pants__cuff__type__CuffSkirt",
    "pants__cuff__type__CuffBandSkirt",
    "pants__cuff__type__None"
  ],
  "pants__cuff__top_ruffle": [
    "pants__cuff__top_ruffle__none",
    "pants__cuff__top_ruffle__moderate",
    "pants__cuff__top_ruffle__rich"
  ],
  "pants__cuff__cuff_len": [
    "pants__cuff__cuff_len__short",
    "pants__cuff__cuff_len__medium",
    "pants__cuff__cuff_len__long"
  ],
  "pants__cuff__skirt_fraction": [
    "pants__cuff__skirt_fraction__small",
    "pants__cuff__skirt_fraction__medium",
    "pants__cuff__skirt_fraction__large"
  ],
  "pants__cuff__skirt_flare": [
    "pants__cuff__skirt_flare__slight",
    "pants__cuff__skirt_flare__moderate",
    "pants__cuff__skirt_flare__significant"
  ],
  "pants__cuff__skirt_ruffle": [
    "pants__cuff__skirt_ruffle__none",
    "pants__cuff__skirt_ruffle__some"
  ]
}

def list_to_prefix_dict(strings):
    """
    Converts the list of strings to a dictionary of Prefix -> Original String List (in the order in which it appears).
    A prefix refers to the part after the last '__' segment is removed.
    """
    result = OrderedDict()
    for s in strings:
        parts = s.split(CONNECT_TAG)
        prefix = CONNECT_TAG.join(parts[:-1])  # Remove the last fragment
        if prefix not in result:
            result[prefix] = []
        result[prefix].append(s)  # Put the full string in
    return result
def input_caption2random_default_cption(test_gpt_caption=None):
    '''all_text_dict: dict is the dict of the text space, and it is ordered,
    which can guarantee the order (because the network is trained to ensure the order)
    test_gpt_caption:list is the list of gpt_caption, here there is no specific order,
    Below, the text in the test_gpt_caption will be retained, and the others will be randomly selected,
     and the order will be guaranteed, and a list will be returned'''
    test_gpt_caption_list=list_to_prefix_dict(test_gpt_caption)
    random_list = []
    for key ,value_list in all_text_dict.items():
        # if key == 'levels-skirt__base':
        #     print(value_list)
        if key not in test_gpt_caption_list:
            if key == 'shirt__length':
                random_list.append("shirt__length__super-cropped")
            elif key == 'pants__cuff__type':
                random_list.append("pants__cuff__type__None")
            elif key == "sleeve__cuff__type":
                random_list.append("sleeve__cuff__type__None")
            elif key == "left__sleeve__cuff__type":
                random_list.append("left__sleeve__cuff__type__None")
            elif key == 'collar__component__style':
                random_list.append("collar__component__style__None")
            elif key == "pencil-skirt__low_angle":
                random_list.append("pencil-skirt__low_angle__straight")
            elif key == "sleeve__connecting_width":
                random_list.append("sleeve__connecting_width__medium")
            elif key == "sleeve__end_width":
                random_list.append("sleeve__end_width__straight")
            elif key == "left__sleeve__connecting_width":
                random_list.append("left__sleeve__connecting_width__medium")
            elif key == "left__sleeve__end_width":
                random_list.append("left__sleeve__end_width__straight")
            elif 'False' in value_list[0] or 'True' in value_list[0]:
                random_list.append(value_list[1])
            else:
                chice_num=random.randint(0,len(value_list)-1)
                random_list.append(value_list[chice_num])
        else:
            if test_gpt_caption_list[key][0] in value_list:
                res= test_gpt_caption_list[key][0]
                random_list.append(res)
            else:
              chice_num = random.randint(0, len(value_list) - 1)
              random_list.append(value_list[chice_num])


    return random_list
def vec_2_pattern_yaml(yaml_data,param_vec,mask_list):
  yaml_file_name = None
  pattern_data_dict = {}
  pattern_vec = {}
  cont = 0
  param_vec = np.clip(param_vec, 0, 1)


  def extract_new_vec_v2v(data, path=''):
    """
    Recursively traverses the data structure and extracts all the 'v' values.
    :p aram data: YAML loaded data
    :p aram path: The path of the current field, which is used to display the hierarchy
    :return: No return value, print directly
    """
    nonlocal cont
    nonlocal param_vec
    nonlocal mask_list
    if isinstance(data, dict):
      for key, value in data.items():
        # If the key is 'v', the path and the corresponding value are printed
        if key == 'v':
          range = data['range']

          if mask_list[cont] == 0 or data['v'] == 0:
            cont = cont + 1
            continue
          elif data['type'] == 'select_null' or data['type'] == 'select':
            pass
          elif data['type'] == 'bool':
            pass
          elif data['type'] == 'int':
            re_normal_value = param_vec[cont] * (range[1] - range[0]) + range[0]
            data['v'] = int(re_normal_value)
          elif data['type'] == 'float':
            re_normal_value = param_vec[cont] * (range[1] - range[0]) + range[0]
            data['v'] = float(re_normal_value*mask_list[cont])

          cont = cont + 1
        else:
          # Recursively moves on to the next layer
          extract_new_vec_v2v(value, path + key + '.')
  extract_new_vec_v2v(yaml_data, path='')
  return yaml_data

class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

def save_design2yaml(design, new_yaml_path):
    garment_param = {'design': design}
    new_yaml_path_dir = os.path.dirname(new_yaml_path)
    os.makedirs(new_yaml_path_dir, exist_ok=True)

    with open(new_yaml_path, 'w') as yaml_file:
        yaml.dump(garment_param, yaml_file, default_flow_style=False, allow_unicode=True, sort_keys=False,
                  Dumper=NoAliasDumper)