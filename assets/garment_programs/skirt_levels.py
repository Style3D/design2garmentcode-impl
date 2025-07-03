from assets.garment_programs.circle_skirt import *
from assets.garment_programs.skirt_paneled import *
from copy import deepcopy


class SkirtLevels(BaseBottoms):
    """Skirt constiting of multuple stitched skirts"""

    def __init__(self, body, design, rise=None) -> None:
        super().__init__(body, design, rise=rise)

        ldesign = design['levels-skirt']
        lbody = deepcopy(body)  # We will modify the values, so need a copy
        n_levels = ldesign['num_levels']['v']
        ruffle = ldesign['level_ruffle']['v']

        # Adjust length to the common denominators
        self.eval_length(ldesign, body)
        
        # Definitions
        self.rise = ldesign['rise']['v'] if rise is None else rise
        base_skirt_class = globals()[ldesign['base']['v']]
        self.subs.append(base_skirt_class(
            body, 
            design, 
            length=self.base_len, 
            rise=self.rise,
            slit=False))

        if (hasattr(base := self.subs[0], 'design')
                and 'low_angle' in base.design):
            self.angle = base.design['low_angle']['v']
        else:
            self.angle = 0

        # Place the levels
        level_skirt_class = globals()[ldesign['level']['v']]
        for i in range(n_levels):
            # Adjust the mesurement to trick skirts into producing correct width
            # TODOLOW More elegant overwrite
            lbody['waist'] = ruffle * self.subs[-1].interfaces['bottom'].edges.length()
            lbody['waist_back_width'] = ruffle * self.subs[-1].interfaces['bottom_b'].edges.length()
            self.subs.append(level_skirt_class(
                lbody, 
                design, 
                tag=str(i), 
                length=self.level_len, 
                slit=False,
                top_ruffles=False))

            # Placement
            # Rotation if base is assymetric
            self.subs[-1].rotate_by(R.from_euler(
                'XYZ', [0, 0, -self.angle], degrees=True))

            self.subs[-1].place_by_interface(
                self.subs[-1].interfaces['top'],
                self.subs[-2].interfaces['bottom'], 
                gap=5
            )
            # Stitch
            self.stitching_rules.append((
                self.subs[-2].interfaces['bottom'], 
                self.subs[-1].interfaces['top']
            ))

        self.interfaces = {
            'top': self.subs[0].interfaces['top']
        }

    def eval_length(self, ldesign, body):
        
        # With convertion to absolute values
        total_length = ldesign['length']['v'] * body['_leg_length']
        self.base_len = total_length * ldesign['base_length_frac']['v']
        self.level_len = (total_length - self.base_len) / ldesign['num_levels']['v']

        # Add hip_line (== zero length)
        self.base_len = body['hips_line'] * ldesign['rise']['v'] + self.base_len


class SkirtLayers(BaseBottoms):
    """Skirt consisting of multiple layered skirts stitched at the waistline"""

    def __init__(self, body, design, rise=None):
        super().__init__(body, design, rise=rise)

        ldesign = design['layers-skirt']
        lbody = deepcopy(body)  # We will modify the values, so need a copy
        n_layers = ldesign['num_layers']['v']
        ruffle = ldesign['layer_ruffle']['v']

        # Definitions
        self.rise = ldesign['rise']['v'] if rise is None else rise
        base_skirt_class = globals()[ldesign['base']['v']]

        total_length = ldesign['length']['v'] * body['_leg_length']
        layer_lengths = self.eval_layer_lengths(ldesign, total_length, n_layers)
        # Place the levels
        self.layers = []
        for i in range(n_layers):
            # Adjust the measurements to produce correct width with ruffle
            waist_multiplier = 1 + ruffle * i
            lbody['waist'] = self.body['waist'] * waist_multiplier
            lbody['waist_back_width'] = self.body['waist_back_width'] * waist_multiplier
            layer_length = layer_lengths[i]
            skirt_layer = base_skirt_class(
                lbody, 
                design, 
                tag=str(i), 
                length=layer_length, 
                rise=self.rise,
                slit=False,
                top_ruffles=False)

            # Place the layer at the waistline
            skirt_layer.translate_by([0, self.body['_waist_level'], 0])

            self.layers.append(skirt_layer)

        # Interfaces
        self.interfaces = {
            'top': self.layers[0].interfaces['top'],
            'bottom': self.layers[-1].interfaces['bottom']
        }

        # Stitching rules: stitch each outer layer's top interface 
        # to the 'top' interface of the component (waistline)

        for layer in self.layers[1:]:
            self.stitching_rules.append(
                (self.interfaces['top'], layer.interfaces['top'])
            )


        # Add layers to subcomponents
        self.subs.extend(self.layers)
        for id,layer in enumerate(self.layers):
            layer.front.translate_by([0,0, 5*id])
            layer.back.translate_by([0, 0, -5*id])

    def eval_layer_lengths(self, ldesign, total_length, n_layers):
        """Calculate lengths for each layer"""
        if 'layer_lengths' in ldesign:
            # If specific lengths are provided for each layer
            layer_lengths = [ldesign['layer_lengths'][i]['v'] * total_length for i in range(n_layers)]
        else:
            # Distribute the total length among layers, possibly making outer layers longer
            base_length = total_length / n_layers
            layer_lengths = [base_length * (1 + 0.1 * i) for i in range(n_layers)]
        return layer_lengths