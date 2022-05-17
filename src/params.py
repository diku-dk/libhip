import yaml

"""
Cartilage generation parameters

Sets the parameter of the joint for future cartilage generation.

@param neighbourhood_size: How far away (in terms of edges) a vertex can be, while still considered
a neighbour. Also referred to as 'k-ring' in some literature.
@param curvature_type: choose between "gaussian", "mean", "minimum", "maximum"
Refers to the gaussian, mean, the maximum and the minimum of the principal curvatures, respectively.
@param gap_distance: The distance between the primary bone and the secondaries.
@param trimming_iteration: number of times the trimming step should be performed.
@param min_curvature_threshold: The minimum curvature where we will consider the surface to be part of the cartilage
@param max_curvature_threshold: The maximum curvature where we will consider the surface to be part of the cartilage
@param blending_order: Order of the harmonic weight computation during cartilage generation.
@param smoothing_factor: The size of the smoothing step (this is similar to the 'h' parameter in mean curvature flow)
@param smoothing_iteration_base: The number of times the smoothing step should be performed on the base layer.
@param smoothing_iteration_extruded_base: The number of times the smoothing step should be performed on the extruded layer.
@param output_dimension: The scale of the output ("mm" = millimeters, "m" = meters).
@param thickness_factor: a constant which will be multiplied by the distance between two surfaces.This allows you to 
control the thickness value.
"""
# class SubInfo:
#     def __init__(self, config):
#         self.subject_id: str = config["subject"]["subject_id"]

class LhjAc:
    def __init__(self, config):
        self.gap_distance: float = config["lhj_ac_var"]["gap_distance"]
        self.trimming_iteration: int = config["lhj_ac_var"]["trimming_iteration"]
        self.smoothing_factor: float = config["lhj_ac_var"]["smoothing_factor"]
        self.smoothing_iteration_base: int = config["lhj_ac_var"]["smoothing_iteration_base"]
        self.no_extend_trimming_iteration: int = config["lhj_ac_var"]["no_extend_trimming_iteration"]
        self.w_gap_thickness_factor: float = config["lhj_ac_var"]["w_gap_thickness_factor"]
        self.wo_gap_thickness_factor: float = config["lhj_ac_var"]["wo_gap_thickness_factor"]
        self.bandwidth: float = config["lhj_ac_var"]["bandwidth"]
        self.blending_order: int = config["lhj_ac_var"]["blending_order"]
        self.full_model = config["lhj_ac_var"]["full_model"]
        self.subject_id: str = config["lhj_ac_var"]["subject_id"]

class LhjFc:
    def __init__(self, config):
        self.trimming_iteration: int = config["lhj_fc_var"]["trimming_iteration"]
        self.neighbourhood_size: int = config["lhj_fc_var"]["neighbourhood_size"]
        self.curvature_type: str = config["lhj_fc_var"]["curvature_type"]
        self.curve_info = config["lhj_fc_var"]["curve_info"]
        self.min_curvature_threshold: float = config["lhj_fc_var"]["min_curvature_threshold"]
        self.max_curvature_threshold: float = config["lhj_fc_var"]["max_curvature_threshold"]
        self.trimming_base_iteration: int = config["lhj_fc_var"]["trimming_base_iteration"]
        self.smoothing_factor: float = config["lhj_fc_var"]["smoothing_factor"]
        self.smoothing_iteration_base: int = config["lhj_fc_var"]["smoothing_iteration_base"]
        self.w_gap_thickness_factor: float = config["lhj_fc_var"]["w_gap_thickness_factor"]
        self.wo_gap_thickness_factor: float = config["lhj_fc_var"]["wo_gap_thickness_factor"]
        self.bandwidth: float = config["lhj_fc_var"]["bandwidth"]
        self.blending_order: int = config["lhj_fc_var"]["blending_order"]
        self.full_model = config["lhj_fc_var"]["full_model"]
        self.subject_id: str = config["lhj_fc_var"]["subject_id"]

class Lsj:
    def __init__(self, config):
        self.gap_distance: float = config["lsj_var"]["gap_distance"]
        self.trimming_iteration_p: int = config["lsj_var"]["trimming_iteration_p"]
        self.smoothing_iteration_base: int = config["lsj_var"]["smoothing_iteration_base"]
        self.smoothing_factor: float = config["lsj_var"]["smoothing_factor"]
        self.fix_boundary = config["lsj_var"]["fix_boundary"]
        self.trimming_iteration_s: int = config["lsj_var"]["trimming_iteration_s"]
        self.smoothing_iteration_extruded_base: int = config["lsj_var"]["smoothing_iteration_extruded_base"]
        self.upsampling_iteration: int = config["lsj_var"]["upsampling_iteration"]
        self.full_model = config["lsj_var"]["full_model"]
        self.subject_id: str = config["lsj_var"]["subject_id"]

class RhjAc:
    def __init__(self, config):
        self.gap_distance: float = config["rhj_ac_var"]["gap_distance"]
        self.trimming_iteration: int = config["rhj_ac_var"]["trimming_iteration"]
        self.smoothing_factor: float = config["rhj_ac_var"]["smoothing_factor"]
        self.smoothing_iteration_base: int = config["rhj_ac_var"]["smoothing_iteration_base"]
        self.no_extend_trimming_iteration: int = config["rhj_ac_var"]["no_extend_trimming_iteration"]
        self.w_gap_thickness_factor: float = config["rhj_ac_var"]["w_gap_thickness_factor"]
        self.wo_gap_thickness_factor: float = config["rhj_ac_var"]["wo_gap_thickness_factor"]
        self.bandwidth: float = config["rhj_ac_var"]["bandwidth"]
        self.blending_order: int = config["rhj_ac_var"]["blending_order"]
        self.full_model = config["rhj_ac_var"]["full_model"]
        self.subject_id: str = config["rhj_ac_var"]["subject_id"]

class RhjFc:
    def __init__(self, config):
        self.trimming_iteration: int = config["rhj_fc_var"]["trimming_iteration"]
        self.neighbourhood_size: int = config["rhj_fc_var"]["neighbourhood_size"]
        self.curvature_type: str = config["rhj_fc_var"]["curvature_type"]
        self.curve_info = config["rhj_fc_var"]["curve_info"]
        self.min_curvature_threshold: float = config["rhj_fc_var"]["min_curvature_threshold"]
        self.max_curvature_threshold: float = config["rhj_fc_var"]["max_curvature_threshold"]
        self.trimming_base_iteration: int = config["rhj_fc_var"]["trimming_base_iteration"]
        self.smoothing_factor: float = config["rhj_fc_var"]["smoothing_factor"]
        self.smoothing_iteration_base: int = config["rhj_fc_var"]["smoothing_iteration_base"]
        self.w_gap_thickness_factor: float = config["rhj_fc_var"]["w_gap_thickness_factor"]
        self.wo_gap_thickness_factor: float = config["rhj_fc_var"]["wo_gap_thickness_factor"]
        self.bandwidth: float = config["rhj_fc_var"]["bandwidth"]
        self.blending_order: int = config["rhj_fc_var"]["blending_order"]
        self.full_model = config["rhj_fc_var"]["full_model"]
        self.subject_id: str = config["rhj_fc_var"]["subject_id"]

class Rsj:
    def __init__(self, config):
        self.gap_distance: float = config["rsj_var"]["gap_distance"]
        self.trimming_iteration_p: int = config["rsj_var"]["trimming_iteration_p"]
        self.smoothing_iteration_base: int = config["rsj_var"]["smoothing_iteration_base"]
        self.smoothing_factor: float = config["rsj_var"]["smoothing_factor"]
        self.fix_boundary = config["rsj_var"]["fix_boundary"]
        self.trimming_iteration_s: int = config["rsj_var"]["trimming_iteration_s"]
        self.smoothing_iteration_extruded_base: int = config["rsj_var"]["smoothing_iteration_extruded_base"]
        self.upsampling_iteration: int = config["rsj_var"]["upsampling_iteration"]
        self.full_model = config["rsj_var"]["full_model"]
        self.subject_id: str = config["rsj_var"]["subject_id"]

class Pj:
    def __init__(self, config):
        self.gap_distance: float = config["pj_var"]["gap_distance"]
        self.trimming_iteration_p: int = config["pj_var"]["trimming_iteration_p"]
        self.trimming_iteration_s: int = config["pj_var"]["trimming_iteration_s"]
        self.smoothing_iteration_base: int = config["pj_var"]["smoothing_iteration_base"]
        self.smoothing_factor: float = config["pj_var"]["smoothing_factor"]
        self.fix_boundary = config["pj_var"]["fix_boundary"]
        self.smoothing_iteration_extruded_base: int = config["pj_var"]["smoothing_iteration_extruded_base"]
        self.upsampling_iteration: int = config["pj_var"]["upsampling_iteration"]
        self.full_model = config["pj_var"]["full_model"]
        self.subject_id: str = config["pj_var"]["subject_id"]

class VolGen:
    def __init__(self, config):
        self.epsilon_coarse: str = config["vol_var"]["epsilon_coarse"]
        self.epsilon_fine: str = config["vol_var"]["epsilon_fine"]
        self.edge_length_leg_coarse: str = config["vol_var"]["edge_length_leg_coarse"]
        self.edge_length_girdle_coarse: str = config["vol_var"]["edge_length_girdle_coarse"]
        self.edge_length_leg_fine: str = config["vol_var"]["edge_length_leg_fine"]
        self.edge_length_girdle_fine: str = config["vol_var"]["edge_length_girdle_fine"]

class SimGen:
    def __init__(self, config):
        self.lf_z_coord: float = config["sim_var"]["lf_z_coord"]
        self.rf_z_coord: float = config["sim_var"]["rf_z_coord"]

class Config:

    def __init__(self, config_path):
        self.config = None
        with  open(config_path) as fd:
            self.config = yaml.safe_load(fd)
        self.lhj_ac_var = LhjAc(self.config)
        self.lhj_fc_var = LhjFc(self.config)
        self.lsj_var = Lsj(self.config)
        self.rhj_ac_var = RhjAc(self.config)
        self.rhj_fc_var = RhjFc(self.config)
        self.rsj_var = Rsj(self.config)
        self.pj_var = Pj(self.config)
        self.vol_var = VolGen(self.config)
        self.sim_var = SimGen(self.config)
        # self.subject = SubInfo(self.config)

# if __name__ == "__main__":
#     print("hello")
#     config = Config ("../config/m1_config.yml")
#     print(config.hj_ac_var.gap_distance)
