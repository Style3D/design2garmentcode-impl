from assets.garment_programs.tee import *
from assets.garment_programs.godet import *
from assets.garment_programs.bodice import *
from assets.garment_programs.pants import *
from assets.garment_programs.bands import *
from assets.garment_programs.skirt_paneled import *
from assets.garment_programs.skirt_levels import *
from assets.garment_programs.circle_skirt import *
from assets.garment_programs.sleeves import *
import yaml
class TotalLengthError(BaseException):
    """Error indicating that the total length of a garment goes beyond 
    the floor length for a given person"""
    pass

class IncorrectElementConfiguration(BaseException):
    """Error indicating that given pattern is an empty garment"""
    pass

class MetaGarment(pyg.Component):
    """Meta garment component
        Depending on parameter values it can generate sewing patterns
    for various dresses and jumpsuit styles and fit them to the body
    measurements
    """

    def __init__(self, name, body, design) -> None:
        super().__init__(name)
        self.body = body
        self.design = design
        # with open('assets/bodies/mean_all_full.yaml', 'w') as f:
        #     yaml.dump(body, f, default_flow_style=False)
        # Elements
        self.upper_name = design['meta']['upper']['v']
        self.lower_name = design['meta']['bottom']['v']
        self.belt_name = design['meta']['wb']['v']

        # Upper garment
        if self.upper_name:
            upper = globals()[self.upper_name]
            self.subs = [upper(body, design)]

            # Set a label
            self.subs[-1].set_panel_label('body', overwrite=False)

            #Pan up a bit：
            self.subs[-1].translate_by((0, 5, 0))

        # Here are all the garments that are not connected to have a belt
        if self.belt_name == None:
            if design['meta']['connected']['v'] == False and design['meta']['bottom']['v'] != None:
                if design['meta']['bottom']['v'] != 'Pants':
                    design['meta']['wb']['v'] = "FittedWB"
                    design['waistband']['waist']['v'] = 0.7
                    design['waistband']['width']['v'] = 0.1
                if design['meta']['bottom']['v'] == 'Pants':
                    design['meta']['wb']['v'] = 'FittedWB'
                    design['waistband']['waist']['v'] = 1
                    design['waistband']['width']['v'] = 0.2
                self.belt_name = design['meta']['wb']['v']

        # Define Lower garment
        if self.lower_name:
            Lower_class = globals()[self.lower_name]
            # NOTE: full rise for fitted tops
            Lower = Lower_class(body, design, rise=1. if self.upper_name and 'Fitted' in self.upper_name else None)
        else:
            Lower = None
        # Belt (or not)
        # TODO Adapt the rise of the lower garment to the width of the belt for correct matching
        if self.belt_name:
            Belt_class = globals()[self.belt_name]

            # Adjust rise to match the Lower garment if needed
            Belt = Belt_class(body, design, Lower.get_rise() if Lower else 1.)

            self.subs.append(Belt)
            # Place below the upper garment
            if len(self.subs) > 1:
                self.subs[-1].place_by_interface(
                    self.subs[-1].interfaces['top'],
                    self.subs[-2].interfaces['bottom'],
                    gap=5
                )
                if design['meta']['connected']['v'] :  # If you need to connect, you need to connect the belt to the top
                    self.stitching_rules.append(
                        (self.subs[-2].interfaces['bottom'],
                         self.subs[-1].interfaces['top']))
            # Add waist label
            self.subs[-1].interfaces['top'].edges.propagate_label('lower_interface')
            # Set panel segmentation labels
            self.subs[-1].set_panel_label('body', overwrite=False)
        if self.lower_name:
            self.subs.append(Lower)
            # Place below the upper garment or self.wb
            if len(self.subs) > 1:
                self.subs[-1].place_by_interface(
                    self.subs[-1].interfaces['top'],
                    self.subs[-2].interfaces['bottom'],
                    gap=5
                )
                #There must be a belt now, so here's how to connect the belt to the bottom
                self.stitching_rules.append(
                    (self.subs[-2].interfaces['bottom'],
                     self.subs[-1].interfaces['top']))
                #To deal with the simulation impact caused by the lack of connection, the main thing is to adjust the position and all the next translationby is to simulate better and reduce the problem situation.
                # The specific tranlateby values are mainly tried
                if not design['meta']['connected']['v']:
                    self.handle_disconnected_position_influence(design)
            # Add waist label
            if not self.belt_name:
                self.subs[-1].interfaces['top'].edges.propagate_label('lower_interface')
            # Set panel segmentation labels
            self.subs[-1].set_panel_label('leg', overwrite=False)



    def handle_disconnected_position_influence(self, design):
        '''deal with the influence of disconnected garments on the simulation by translateby .
        which is value is tried out'''
        self.subs[-1].translate_by((0, 6, 0))
        # Gets a specific clothing object
        pant_flag = False
        pant = None
        circleskirt = None
        circleskirt_flag = False
        shirt = None
        shirt_flag = False
        for sub in self.subs:
            if isinstance(sub, Pants):
                pant_flag = True
                pant = sub
            if isinstance(sub, SkirtCircle):
                circleskirt = sub
                circleskirt_flag = True
            if isinstance(sub, Shirt):
                shirt = sub
                shirt_flag = True
        if pant_flag and shirt_flag:

            # If the top is short<=1.2, you need to pan the pants downward.
            if design['shirt']['length']['v'] <= 1.2:
                # pass
                pant.translate_by((0, -13, 0))
            # For clothes that are too long, pull them up
            if design['shirt']['length'][
                'v'] > 1.2:
                pant.translate_by((0, 25, 0))
                translate_d = 8
                shirt.right.ftorso.translate_by((0, 0, translate_d))
                shirt.right.btorso.translate_by((0, 0, -translate_d))
                shirt.left.ftorso.translate_by((0, 0, translate_d))
                shirt.left.btorso.translate_by((0, 0, -translate_d))
        # For the handling that is not underwear
        if design['meta']['bottom']['v'] is not None and design['meta']['bottom']['v'] != 'Pants':
            translate_d = 10
            bottom_garment = self.subs[-1]
            # if design['meta']['bottom']['v'] != "SkirtManyPanels":
            #     bottom_garment.translate_by((0, 0, 0))
            # Deal with a single class first, for multiple skirts such as level, this is not processed, and later, at present, multi-layer group skirts do not need to be processed
            if (design['meta']['bottom']['v'] == "Skirt2 " or design['meta']['bottom']['v'] == "SkirtCircle"
                    or design['meta']['bottom']['v'] == "AssymmSkirtCircle"
                    or design['meta']['bottom']['v'] == "PencilSkirt"):
                bottom_garment.front.translate_by((0, 0, translate_d))
                bottom_garment.back.translate_by((0, 0, -translate_d))
            bottom_garment.translate_by((0, -8, 0))
        # For the handling of the pants
        if pant_flag:
            pant.translate_by((0, -8, 0))


    def assert_total_length(self, tol=1):
        """Check the total length of components"""
        # Check that the total length of the components are less that body height
        length = self.length()
        floor = self.body['height'] - self.body['head_l']
        if length > floor + tol:
            raise TotalLengthError(f'{self.__class__.__name__}::{self.name}::ERROR:'
                                    f':Total length {length} exceeds the floor length {floor}')

    # TODO these checks don't require initialization of the pattern!
    def assert_non_empty(self, filter_belts=True):
        """Check that the garment is non-empty
            * filter_wb -- if set, then garments consisting only of waistbands are considered empty
        """
        if not self.upper_name and not self.lower_name:
            if filter_belts or not self.belt_name:
                raise IncorrectElementConfiguration()

    def assert_skirt_waistband(self):
        """Check if a generated heavy skirt is created with a waistband"""

        if self.lower_name and self.lower_name in ['SkirtCircle', 'AsymmSkirtCircle', 'SkirtManyPanels']:
            if not (self.belt_name or self.upper_name):
                raise IncorrectElementConfiguration()