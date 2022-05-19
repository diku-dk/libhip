import src
import numpy as np
import igl
import meshplot as mp
import math
import matplotlib.pyplot as plt
import pandas as pd
import os

def get_hj_ac(pb_vertices, pb_faces, sb_vertices, sb_faces, param, anatomical_path):

    """
    This function generates the hip joint acetabular cartilage based on the femur and hip bones

    :param pb_vertices: list of vertex positions of the primary bone, referred to as $V_{P}$ in the manuscript
    :param pb_faces: list of triangle indices of the primary bone, referred to as $\F_{P}$ in the manuscript
    :param sb_vertices: list of vertex positions of the secondary bone, referred to as $\V_{S}$ in the manuscript
    :param sb_faces: list of triangle indices of the secondary bone, referred to as $\F_{S}$ in the manuscript
    :param param: list of parameters needed to generate hip joint cartilage models located in the config folder
    :param anatomical_path: path to the joint anatomical measurements

    :return: vertices and faces of hip joint articulating cartilages
    """

    " Step A. Primary interface estimation"

    # primary interface vertices
    p_vertices = np.copy(pb_vertices)
    p_faces = np.copy(pb_faces)
    p_vertex_idxs = np.unique(p_faces.flatten())

    # bone adjacency faces
    face_adjacency, cumulative_sum = igl.vertex_triangle_adjacency(p_faces, len(p_vertices))

    # initial primary interface estimation
    int_p_face_idxs, minimum_dist = src.get_initial_surface(p_vertices,
                                              p_faces,
                                              sb_vertices,
                                              sb_faces,
                                              param.gap_distance)

    # trim the initial primary interface if needed
    if param.trimming_iteration != 0:
        trim_p_face_idxs = src.trim_boundary(p_faces,
                                             int_p_face_idxs,
                                             face_adjacency,
                                             cumulative_sum,
                                             param.trimming_iteration)
    else:
        trim_p_face_idxs = np.copy(int_p_face_idxs)

    # removing extra components
    one_p_face_idxs = src.get_largest_component(p_faces, trim_p_face_idxs)

    # remove ears
    ear_p_face_idxs = np.copy(one_p_face_idxs)

    for i in range(15):
        ear_p_face_idxs = src.remove_ears(p_faces, ear_p_face_idxs)

    # viz
    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh (p_vertices, p_faces[ear_p_face_idxs], c=src.pastel_yellow, shading=src.sh_true)

    # the base of the Acetabular cartilage, referred to as $\F_{C}^{D}$ in the manuscript
    p_face_idxs = np.copy(ear_p_face_idxs)
    boundary_edges = igl.boundary_facets(p_faces[p_face_idxs])

    # separate and smooth
    if param.smoothing_iteration_base != 0:
        p_vertices = src.smooth_and_separate_boundaries(p_vertices,
                                                        boundary_edges,
                                                        pb_vertices,
                                                        pb_faces,
                                                        param.smoothing_factor,
                                                        param.smoothing_iteration_base)

    # remove penetration/gap to the primary bone
    p_vertices = src.snap_to_surface(p_vertices, pb_vertices, pb_faces)

    # viz
    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh (p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)

    ' Step B. Secondary interface definition in two versions, with and without gap in the hip joint'

    # secondary face interface, referred to as $\F_{C}^{E}$ in the manuscript
    s_faces = np.copy (p_faces)
    s_face_idxs = np.copy (p_face_idxs)
    s_vertex_idxs = np.unique(s_faces[s_face_idxs].flatten())

    s_edge_vertex_idxs = igl.boundary_facets(s_faces[s_face_idxs])
    s_edge_vertex_idxs = np.unique(s_edge_vertex_idxs.flatten())

    # geodesic distance from all the points on the primary bone to the boundary of the secondary interface
    dist_to_s_boundary= igl.exact_geodesic(p_vertices, s_faces, s_edge_vertex_idxs, p_vertex_idxs)

    # select the first subset of the secondary interface $\F_{C}^{D}$ to extrude
    if param.no_extend_trimming_iteration != 0:
        int_s1_face_idxs = src.trim_boundary(s_faces,
                                         s_face_idxs,
                                         face_adjacency,
                                         cumulative_sum,
                                         param.no_extend_trimming_iteration)
    else:
        int_s1_face_idxs = np.copy(s_face_idxs)

    # remove ears
    ear_s1_face_idxs = np.copy(int_s1_face_idxs)
    for i in range(15):
        ear_s1_face_idxs = src.remove_ears(s_faces, ear_s1_face_idxs)

    s1_face_idxs = np.copy (ear_s1_face_idxs)

    # assign a thickness profile to the first subset (s1)
    # with gap
    s_thickness_profile_w_gap, s_minimum_height_w_gap = src.assign_thickness(p_vertices,
                                                                             p_faces,
                                                                             sb_vertices,
                                                                             sb_faces,
                                                                             s_face_idxs,
                                                                             param.w_gap_thickness_factor)

    # without gap
    s_thickness_profile_wo_gap, s_minimum_height_wo_gap = src.assign_thickness(p_vertices,
                                                                               p_faces,
                                                                               sb_vertices,
                                                                               sb_faces,
                                                                               s_face_idxs,
                                                                               param.wo_gap_thickness_factor)

    print('minimum thickness in the initial layer with gap', np.round(s_minimum_height_w_gap, 5))
    print('minimum thickness in the initial layer without gap', np.round(s_minimum_height_wo_gap, 5))

    # select the second subset of the secondary interface (s2)) and extrude
    # w_gap
    s2_w_gap_vertex_idxs = []
    for count, value in enumerate(dist_to_s_boundary):
        if value <= param.bandwidth:
            s_thickness_profile_w_gap[count] = s_minimum_height_w_gap * np.sin(value * np.pi / (2 * param.bandwidth))
            s2_w_gap_vertex_idxs.append(count)

    s2_w_gap_vertex_idxs = np.intersect1d(s_vertex_idxs, np.array(s2_w_gap_vertex_idxs))

    # find the corresponding faces of these vertices
    s2_w_gap_face_idxs = []
    for j in s2_w_gap_vertex_idxs:
        for k in range(cumulative_sum[j], cumulative_sum[j + 1]):
            s2_w_gap_face_idxs += [face_adjacency[k]]

    s2_w_gap_face_idxs = np.intersect1d(s_face_idxs, np.array(s2_w_gap_face_idxs))

    # wo_gap
    s2_wo_gap_vertex_idxs = []
    for count, value in enumerate(dist_to_s_boundary):
        if value <= param.bandwidth:
            s_thickness_profile_wo_gap[count] = s_minimum_height_wo_gap * np.sin(value * np.pi / (2 * param.bandwidth))
            s2_wo_gap_vertex_idxs.append(count)

    s2_wo_gap_vertex_idxs = np.intersect1d(s_vertex_idxs, np.array(s2_wo_gap_vertex_idxs))

    " Step C. closed the cartilage using Harmonic boundary blending "

    # external boundary to be set to the sin function
    # s2_w_gap_vertex_idxs
    # s2_wo_gap_vertex_idxs

    # internal boundary to be set to the thickness
    internal_vertex_idxs = np.unique(s_faces[s1_face_idxs].flatten())

    # we compute a blended extrusion on the remaining of $\faces_{C}^{E}$ which we did not initially select for extrusion
    # with gap
    harmonic_weights_w_gap = src.boundary_value(p_vertices,
                                                s_faces,
                                                s2_w_gap_vertex_idxs,
                                                internal_vertex_idxs,
                                                s_thickness_profile_w_gap,
                                                param.blending_order)

    # without gap
    harmonic_weights_wo_gap = src.boundary_value(p_vertices,
                                                 s_faces,
                                                 s2_wo_gap_vertex_idxs,
                                                 internal_vertex_idxs,
                                                 s_thickness_profile_wo_gap,
                                                 param.blending_order)

    # we make sure the thickness is not exceeding the thickness factor limit by putting a limit to extrusion
    # with gap
    s_maximum_thickness_allowed_w_gap, _ = src.assign_thickness(p_vertices,
                                                                s_faces,
                                                                sb_vertices,
                                                                sb_faces,
                                                                s_face_idxs,
                                                                param.w_gap_thickness_factor)
    # without gap
    s_maximum_thickness_allowed_wo_gap, _ = src.assign_thickness(p_vertices,
                                                                 s_faces,
                                                                 sb_vertices,
                                                                 sb_faces,
                                                                 s_face_idxs,
                                                                 param.wo_gap_thickness_factor)

    for i in s_vertex_idxs:
        if harmonic_weights_w_gap[i] > np.max(s_maximum_thickness_allowed_w_gap):
            harmonic_weights_w_gap[i] = np.max(s_maximum_thickness_allowed_w_gap)

    harmonic_weights_w_gap = harmonic_weights_w_gap[s_vertex_idxs]
    harmonic_weights_wo_gap = harmonic_weights_wo_gap[s_vertex_idxs]

    # extrude surface
    s_vertices_w_gap = src.extrude_cartilage(p_vertices,
                                             p_faces,
                                             s_face_idxs,
                                             harmonic_weights_w_gap)

    s_vertices_wo_gap = src.extrude_cartilage(p_vertices,
                                              p_faces,
                                              s_face_idxs,
                                              harmonic_weights_wo_gap)

    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_true)
    frame.add_mesh(s_vertices_w_gap, s_faces[s1_face_idxs], c=src.pastel_green, shading=src.sh_true)
    frame.add_mesh(s_vertices_w_gap, s_faces[s2_w_gap_face_idxs], c=src.sweet_pink, shading=src.sh_true)

    # flip normals of the bottom surface
    p_faces_flipped = p_faces[p_face_idxs]
    p_faces_flipped[:, [0, 1]] = p_faces_flipped[:, [1, 0]]

    # merge the top and bottom vertices
    ac_vertices_w_gap, ac_faces_w_gap = src.merge_surface_mesh(p_vertices,
                                                               p_faces_flipped,
                                                               s_vertices_w_gap,
                                                               s_faces[s_face_idxs])

    ac_vertices_wo_gap, ac_faces_wo_gap = src.merge_surface_mesh(p_vertices,
                                                                 p_faces_flipped,
                                                                 s_vertices_wo_gap,
                                                                 s_faces[s_face_idxs])

    # clean output
    ac_vertices_w_gap, ac_faces_w_gap   = src.clean(ac_vertices_w_gap, ac_faces_w_gap)
    ac_vertices_wo_gap, ac_faces_wo_gap = src.clean(ac_vertices_wo_gap, ac_faces_wo_gap)

    s_vertices_w_gap, implicit_faces_w_gap = src.clean(s_vertices_w_gap, s_faces[s_face_idxs])
    s_vertices_wo_gap, implicit_faces_wo_gap = src.clean(s_vertices_wo_gap, s_faces[s_face_idxs])

    if param.full_model:
        output_w_gap_vertices  = ac_vertices_w_gap
        output_w_gap_faces     = ac_faces_w_gap
        output_wo_gap_vertices = ac_vertices_wo_gap
        output_wo_gap_faces    = ac_faces_wo_gap
    else:
        output_w_gap_vertices  = s_vertices_w_gap
        output_w_gap_faces     = implicit_faces_w_gap
        output_wo_gap_vertices = s_vertices_wo_gap
        output_wo_gap_faces    = implicit_faces_wo_gap

    # viz
    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_true)
    frame.add_mesh(ac_vertices_w_gap, ac_faces_w_gap, c=src.pastel_orange, shading=src.sh_true)

    # visualizing normals
    # centroids, end_points = src.norm_visualization(ac_vertices_w_gap, ac_faces_w_gap)

    # frame = mp.plot(ac_vertices_w_gap, ac_faces_w_gap, c=src.pastel_orange, shading=src.sh_true)
    # frame.add_lines(centroids, end_points, shading={"line_color": "aqua"})

    # viz
    mp.plot(ac_vertices_w_gap, ac_faces_w_gap, c=src.pastel_orange, shading=src.sh_true)

    " Step D. stats "

    df = pd.read_csv (str(anatomical_path), encoding = 'utf-8')

    # cartilage area
    cartilage_area = src.get_area(p_vertices, p_faces[p_face_idxs])

    # average thickness-with gap
    thickness_w_gap_num = np.where(harmonic_weights_w_gap == 0)[0]
    harmonic_thick_w_gap = np.delete(harmonic_weights_w_gap, thickness_w_gap_num, axis=0)

    # average thickness-without gap
    thickness_wo_gap_num = np.where(harmonic_weights_wo_gap == 0)[0]
    harmonic_thick_wo_gap = np.delete(harmonic_weights_wo_gap, thickness_wo_gap_num, axis=0)

    df.loc[3, 'Value'] = minimum_dist
    if df.loc[4, 'Value'] == 'empty':
        df.loc[4, 'Value'] = np.round(cartilage_area, 2)
        df.loc[5, 'Value'] = np.round(np.mean(harmonic_thick_w_gap), 2)
        df.loc[6, 'Value'] = np.round(np.mean(harmonic_thick_wo_gap), 2)
    else:
        df.loc[11, 'Value'] = np.round(cartilage_area, 2)
        df.loc[12, 'Value'] = np.round(np.mean(harmonic_thick_w_gap), 2)
        df.loc[13, 'Value'] = np.round(np.mean(harmonic_thick_wo_gap), 2)

    # write to the specific anatomical file for each subject
    df.to_csv(str(anatomical_path), index=False)

    print("minimum cartilage thickness w/wo gap is: ", np.round(np.min(harmonic_thick_w_gap), 2),"/", np.round(np.min(harmonic_thick_wo_gap), 2) )

    # This data will be used later to create the hip joint femoral cartilage
    sb_face_adjacency, sb_cumulative_sum = igl.vertex_triangle_adjacency(sb_faces, len(sb_vertices))

    _, fc_vertex_idxs = src.get_initial_surface2(p_vertices,
                                                 s_faces[ear_s1_face_idxs],
                                                 sb_vertices,
                                                 sb_faces,
                                                 param.gap_distance)
    fc_face_idxs = []
    for j in fc_vertex_idxs:
        for k in range(sb_cumulative_sum[j], sb_cumulative_sum[j + 1]):
            fc_face_idxs += [sb_face_adjacency[k]]
    fc_face_idxs = np.array(fc_face_idxs)

    frame = mp.plot(sb_vertices, sb_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(p_vertices, p_faces[s_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    frame.add_mesh(sb_vertices, sb_faces[fc_face_idxs], c=src.pastel_yellow, shading=src.sh_true)


    # _, intt_vertex_idxs_secondary_def = src.get_initial_surface2(vertices_p,
    #                                                          faces_p[initial_face_idxs],
    #                                                          vertices_s,
    #                                                          faces_s,
    #                                                          param.gap_distance)
    # intt_face_idxs_def = []
    # for j in intt_vertex_idxs_secondary_def:
    #     for k in range(cumulative_sum_s[j], cumulative_sum_s[j + 1]):
    #         intt_face_idxs_def += [face_adjacency_s[k]]
    #
    # intt_face_idxs_def= np.array(intt_face_idxs_def)

    return p_vertices, output_w_gap_vertices, output_w_gap_faces, output_wo_gap_vertices, output_wo_gap_faces, fc_face_idxs


def get_hj_fc(pb_vertices, pb_faces, sb_vertices, sb_faces, int_p_face_idxs, param, anatomical_path):

    """
    This function generates the hip joint femoral cartilage based on the femur and hip bones

    :param pb_vertices: list of vertex positions of the primary bone, referred to as $V_{P}$ in the manuscript
    :param pb_faces: list of triangle indices of the primary bone, referred to as $\F_{P}$ in the manuscript
    :param sb_vertices: list of vertex positions of the secondary bone, referred to as $\V_{S}$ in the manuscript
    :param sb_faces: list of triangle indices of the secondary bone, referred to as $\F_{S}$ in the manuscript
    :param int_p_face_idxs: the initial estimation of the femoral cartilage based on the distance to the hip bone
    :param param: list of parameters needed to generate hip joint cartilage models located in the config folder
    :param anatomical_path: path to the joint anatomical measurements

    :return: vertices and faces of hip joint articulating cartilages
    """

    " Step A. Primary interface estimation"

    # primary interface vertices
    p_vertices = np.copy(pb_vertices)
    p_faces = np.copy(pb_faces)
    p_vertex_idxs = np.unique(p_faces.flatten())

    # bone adjacency faces
    face_adjacency, cumulative_sum = igl.vertex_triangle_adjacency(p_faces, len(p_vertices))

    # trim the initial primary interface if needed
    if param.trimming_iteration != 0:
        trim_p_face_idxs = src.trim_boundary(p_faces,
                                             int_p_face_idxs,
                                             face_adjacency,
                                             cumulative_sum,
                                             param.trimming_iteration)
    else:
        trim_p_face_idxs = np.copy(int_p_face_idxs)

    # removing extra components
    one_p_face_idxs = src.get_largest_component(p_faces, trim_p_face_idxs)

    # remove ears
    ear_p_face_idxs = np.copy(one_p_face_idxs)

    for i in range(15):
        ear_p_face_idxs = src.remove_ears(p_faces, ear_p_face_idxs)

    # viz
    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(p_vertices, p_faces[ear_p_face_idxs], c=src.pastel_yellow, shading=src.sh_true)

    # the initial estimation on the femoral side does not yet comprehensively cover the femoral head.
    # we apply a curvature-based region filling approach to grow the initial guess to the correct portion on the femoral head.

    # bone curvature measures
    curvature_value = src.get_curvature_measures(pb_vertices,
                                                 pb_faces,
                                                 param.neighbourhood_size,
                                                 param.curvature_type,
                                                 param.curve_info)

    # grow cartilage surface
    grow_p_face_idxs = src.grow_cartilage(p_faces,
                                          ear_p_face_idxs,
                                          face_adjacency,
                                          cumulative_sum,
                                          curvature_value,
                                          param.min_curvature_threshold,
                                          param.max_curvature_threshold)
    # trim the base
    if param.trimming_base_iteration != 0:
        trim_grow_p_face_idxs = src.trim_boundary(p_faces,
                                             grow_p_face_idxs,
                                             face_adjacency,
                                             cumulative_sum,
                                             param.trimming_base_iteration)

    # remove ears
    ear_grow_p_face_idxs = np.copy(trim_grow_p_face_idxs)
    for i in range(5):
        ear_grow_p_face_idxs = src.remove_ears(p_faces, ear_grow_p_face_idxs)

    # the base of the Femoral cartilage, referred to as $\F_{C}^{D}$ in the manuscript
    p_face_idxs = np.copy(ear_grow_p_face_idxs)
    boundary_edges = igl.boundary_facets(p_faces[p_face_idxs])

    # separate and smooth
    if param.smoothing_iteration_base != 0:
        p_vertices = src.smooth_and_separate_boundaries(p_vertices,
                                                        boundary_edges,
                                                        pb_vertices,
                                                        pb_faces,
                                                        param.smoothing_factor,
                                                        param.smoothing_iteration_base)

    # remove penetration/gap to the primary bone
    p_vertices = src.snap_to_surface(p_vertices, pb_vertices, pb_faces)

    # viz
    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    frame.add_mesh(p_vertices, p_faces[ear_p_face_idxs], c=src.pastel_yellow, shading=src.sh_true)

    " Step B. Secondary interface definition in two versions, with and without gap in the hip joint"

    # secondary face interface, referred to as $\F_{C}^{E}$ in the manuscript
    s_faces = np.copy(p_faces)
    s_face_idxs = np.copy(p_face_idxs)
    s_vertex_idxs = np.unique(s_faces[s_face_idxs].flatten())

    s_edge_vertex_idxs = igl.boundary_facets(s_faces[s_face_idxs])
    s_edge_vertex_idxs = np.unique(s_edge_vertex_idxs.flatten())

    # geodesic distance from all the points on the primary bone to the boundary of the secondary interface
    dist_to_s_boundary= igl.exact_geodesic(p_vertices, s_faces, s_edge_vertex_idxs, p_vertex_idxs)

    # select the first subset of the secondary interface $\F_{C}^{D}$ to extrude
    s1_face_idxs = np.copy(ear_p_face_idxs)

    # assign a thickness profile to the first subset (s1)
    # with gap
    s_thickness_profile_w_gap, s_minimum_height_w_gap = src.assign_thickness(p_vertices,
                                                                             p_faces,
                                                                             sb_vertices,
                                                                             sb_faces,
                                                                             s1_face_idxs,
                                                                             param.w_gap_thickness_factor)

    # without gap
    s_thickness_profile_wo_gap, s_minimum_height_wo_gap = src.assign_thickness(p_vertices,
                                                                               p_faces,
                                                                               sb_vertices,
                                                                               sb_faces,
                                                                               s1_face_idxs,
                                                                               param.wo_gap_thickness_factor)

    print('minimum thickness in the initial layer with gap', np.round(s_minimum_height_w_gap, 5))
    print('minimum thickness in the initial layer without gap', np.round(s_minimum_height_wo_gap, 5))

    # select the second subset of the secondary interface (s2) and extrude
    # w_gap
    s2_w_gap_vertex_idxs = []
    for count, value in enumerate(dist_to_s_boundary):
        if value <= param.bandwidth:
            s_thickness_profile_w_gap[count] = s_minimum_height_w_gap * np.sin(value * np.pi / (2 * param.bandwidth))
            s2_w_gap_vertex_idxs.append(count)

    s2_w_gap_vertex_idxs = np.intersect1d(s_vertex_idxs, np.array(s2_w_gap_vertex_idxs))

    # find the corresponding faces of these vertices (for visualization)
    s2_w_gap_face_idxs = []
    for j in s2_w_gap_vertex_idxs:
        for k in range(cumulative_sum[j], cumulative_sum[j + 1]):
            s2_w_gap_face_idxs += [face_adjacency[k]]

    s2_w_gap_face_idxs = np.intersect1d(s_face_idxs, np.array(s2_w_gap_face_idxs))

    # wo_gap
    s2_wo_gap_vertex_idxs = []
    for count, value in enumerate(dist_to_s_boundary):
        if value <= param.bandwidth:
            s_thickness_profile_wo_gap[count] = s_minimum_height_wo_gap * np.sin(value * np.pi / (2 * param.bandwidth))
            s2_wo_gap_vertex_idxs.append(count)

    s2_wo_gap_vertex_idxs = np.intersect1d(s_vertex_idxs, np.array(s2_wo_gap_vertex_idxs))

    " Step C. closed the cartilage using Harmonic boundary blending "

    # external boundary to be set to the sin function
    # s2_w_gap_vertex_idxs
    # s2_wo_gap_vertex_idxs

    # internal boundary to be set to the thickness
    internal_vertex_idxs = np.unique(s_faces[s1_face_idxs].flatten())

    # we compute a blended extrusion on the remaining of $\faces_{C}^{E}$ which we did not initially select for extrusion
    # with gap
    harmonic_weights_w_gap = src.boundary_value(p_vertices,
                                                s_faces,
                                                s2_w_gap_vertex_idxs,
                                                internal_vertex_idxs,
                                                s_thickness_profile_w_gap,
                                                param.blending_order)

    # without gap
    harmonic_weights_wo_gap = src.boundary_value(p_vertices,
                                                 s_faces,
                                                 s2_wo_gap_vertex_idxs,
                                                 internal_vertex_idxs,
                                                 s_thickness_profile_wo_gap,
                                                 param.blending_order)

    # we make sure the thickness is not exceeding the thickness factor limit by putting a limit to extrusion
    # with gap
    s_maximum_thickness_allowed_w_gap, _ = src.assign_thickness(p_vertices,
                                                                s_faces,
                                                                sb_vertices,
                                                                sb_faces,
                                                                s_face_idxs,
                                                                param.w_gap_thickness_factor)
    # without gap
    s_maximum_thickness_allowed_wo_gap, _ = src.assign_thickness(p_vertices,
                                                                 s_faces,
                                                                 sb_vertices,
                                                                 sb_faces,
                                                                 s_face_idxs,
                                                                 param.wo_gap_thickness_factor)

    for i in s_vertex_idxs:
        if harmonic_weights_w_gap[i] > np.max(s_maximum_thickness_allowed_w_gap):
            harmonic_weights_w_gap[i] = np.max(s_maximum_thickness_allowed_w_gap)

    harmonic_weights_w_gap = harmonic_weights_w_gap[s_vertex_idxs]
    harmonic_weights_wo_gap = harmonic_weights_wo_gap[s_vertex_idxs]

    # extrude surface
    s_vertices_w_gap = src.extrude_cartilage(p_vertices,
                                             p_faces,
                                             s_face_idxs,
                                             harmonic_weights_w_gap)

    s_vertices_wo_gap = src.extrude_cartilage(p_vertices,
                                              p_faces,
                                              s_face_idxs,
                                              harmonic_weights_wo_gap)

    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_true)
    frame.add_mesh(s_vertices_w_gap, s_faces[s1_face_idxs], c=src.pastel_green, shading=src.sh_true)
    frame.add_mesh(s_vertices_w_gap, s_faces[s2_w_gap_face_idxs], c=src.sweet_pink, shading=src.sh_true)

    # flip normals of the bottom surface
    p_faces_flipped = p_faces[p_face_idxs]
    p_faces_flipped[:, [0, 1]] = p_faces_flipped[:, [1, 0]]

    # merge the top and bottom vertices
    fc_vertices_w_gap, fc_faces_w_gap = src.merge_surface_mesh(p_vertices,
                                                               p_faces_flipped,
                                                               s_vertices_w_gap,
                                                               s_faces[s_face_idxs])

    fc_vertices_wo_gap, fc_faces_wo_gap = src.merge_surface_mesh(p_vertices,
                                                                 p_faces_flipped,
                                                                 s_vertices_wo_gap,
                                                                 s_faces[s_face_idxs])

    # clean output
    fc_vertices_w_gap, fc_faces_w_gap = src.clean(fc_vertices_w_gap, fc_faces_w_gap)
    fc_vertices_wo_gap, fc_faces_wo_gap = src.clean(fc_vertices_wo_gap, fc_faces_wo_gap)

    s_vertices_w_gap, implicit_faces_w_gap = src.clean(s_vertices_w_gap, s_faces[s_face_idxs])
    s_vertices_wo_gap, implicit_faces_wo_gap = src.clean(s_vertices_wo_gap, s_faces[s_face_idxs])

    if param.full_model:
        output_w_gap_vertices = fc_vertices_w_gap
        output_w_gap_faces = fc_faces_w_gap
        output_wo_gap_vertices = fc_vertices_wo_gap
        output_wo_gap_faces = fc_faces_wo_gap
    else:
        output_w_gap_vertices = s_vertices_w_gap
        output_w_gap_faces = implicit_faces_w_gap
        output_wo_gap_vertices = s_vertices_wo_gap
        output_wo_gap_faces = implicit_faces_wo_gap

    # viz
    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_true)
    frame.add_mesh(fc_vertices_w_gap, fc_faces_w_gap, c=src.pastel_orange, shading=src.sh_true)

    # visualizing normals
    # centroids, end_points = src.norm_visualization(ac_vertices_w_gap, fc_faces_w_gap)

    # frame = mp.plot(ac_vertices_w_gap, fc_faces_w_gap, c=src.pastel_orange, shading=src.sh_true)
    # frame.add_lines(centroids, end_points, shading={"line_color": "aqua"})

    # viz
    mp.plot(fc_vertices_w_gap, fc_faces_w_gap, c=src.pastel_orange, shading=src.sh_true)

    " Step D. stats "
    df = pd.read_csv(str(anatomical_path), encoding='utf-8')

    # cartilage area
    cartilage_area = src.get_area(p_vertices, p_faces[p_face_idxs])

    # average thickness-with gap
    thickness_w_gap_num = np.where(harmonic_weights_w_gap == 0)[0]
    harmonic_thick_w_gap = np.delete(harmonic_weights_w_gap, thickness_w_gap_num, axis=0)

    # average thickness-without gap
    thickness_wo_gap_num = np.where(harmonic_weights_wo_gap == 0)[0]
    harmonic_thick_wo_gap = np.delete(harmonic_weights_wo_gap, thickness_wo_gap_num, axis=0)

    # to later fit a sphere to
    anatomical_dir = os.path.dirname(anatomical_path)
    basep_vertex_idxs = np.unique(p_faces[p_face_idxs].flatten())
    subject_id = df.loc[1, 'Value']

    if df.loc[7, 'Value'] == 'empty':
        np.save(anatomical_dir + '/' + str(subject_id) + '_lhj_fc_base_faces', pb_vertices[basep_vertex_idxs])
        df.loc[7, 'Value'] = np.round(cartilage_area, 2)
        df.loc[8, 'Value'] = np.round(np.mean(harmonic_thick_w_gap), 2)
        df.loc[9, 'Value'] = np.round(np.mean(harmonic_thick_wo_gap), 2)
    else:
        np.save(anatomical_dir + '/' + str(subject_id) + '_rhj_fc_base_faces', pb_vertices[basep_vertex_idxs])
        df.loc[14, 'Value'] = np.round(cartilage_area, 2)
        df.loc[15, 'Value'] = np.round(np.mean(harmonic_thick_w_gap), 2)
        df.loc[16, 'Value'] = np.round(np.mean(harmonic_thick_wo_gap), 2)

    # write to the specific anatomical file for each subject
    df.to_csv(str(anatomical_path), index=False)


    #     # to measure thickness
    #     thickness_profile_w_gap_def, _ = src.assign_thickness(vertices_p,
    #                                                           faces_p,
    #                                                           vertices_s,
    #                                                           faces_s,
    #                                                           intt_face_idxs_def,
    #                                                           param.thickness_factor)
    #
    #     thickness_profile_wo_gap_def, _ = src.assign_thickness(vertices_p,
    #                                                            faces_p,
    #                                                            vertices_s,
    #                                                            faces_s,
    #                                                            intt_face_idxs_def,
    #                                                            0.5)
    #
    #     print('max_default_with gap', np.round(np.max(thickness_profile_w_gap_def), 5))
    #     print('max_default_without_gap', np.round(np.max(thickness_profile_wo_gap_def), 5))
    #
    #     print('minimum thickness in the initial layer with gap', np.round(minimum_height_w_gap, 5))
    #     print('minimum thickness in the initial layer without gap', np.round(minimum_height_wo_gap, 5))

    # intt_face_idxs_def
    return p_vertices, output_w_gap_vertices, output_w_gap_faces, output_wo_gap_vertices, output_wo_gap_faces


def get_sj(pb_vertices, pb_faces, sb_vertices, sb_faces, param, anatomical_path):

    """
    This function generates single-piece cartilage for the sacroiliac joint

    :param pb_vertices: list of vertex positions of the primary bone
    :param pb_faces: list of triangle of the primary primary bone
    :param sb_vertices: list of vertex positions of the secondary bone
    :param sb_faces: list of triangle indices of the secondary bone
    :param param: list of parameters needed to generate the cartilage models located in the config folder
    :param anatomical_path: path to the joint anatomical measurements

    :return: vertices and faces of the sacroiliac joint
    """

    " Step A. Primary interface estimation "

    # primary and secondary interface vertices and faces
    p_vertices = np.copy(pb_vertices)
    p_faces = np.copy(pb_faces)
    s_vertices = np.copy(sb_vertices)
    s_faces = np.copy(sb_faces)

    # bone adjacency faces
    face_adjacency_p, cumulative_sum_p = igl.vertex_triangle_adjacency(p_faces, len(p_vertices))
    face_adjacency_s, cumulative_sum_s = igl.vertex_triangle_adjacency(s_faces, len(s_vertices))

    # initial cartilage surface definition
    int_p_face_idxs, _ = src.get_initial_surface(p_vertices, p_faces, sb_vertices, sb_faces, param.gap_distance)

    # trim the cartilage boundary layer
    if param.trimming_iteration_p != 0 :
        trim_p_face_idxs = src.trim_boundary(p_faces,
                                             int_p_face_idxs,
                                             face_adjacency_p,
                                             cumulative_sum_p,
                                             param.trimming_iteration_p)
    else:
        trim_p_face_idxs = np.copy(int_p_face_idxs)

    # removing extra components
    ear_p_face_idxs = src.get_largest_component(p_faces, trim_p_face_idxs)

    # remove ears
    ear_p_face_idxs = np.copy(ear_p_face_idxs)
    for i in range(10):
        ear_p_face_idxs = src.remove_ears(p_faces, ear_p_face_idxs)

    # the primary interface of the sacroiliac joint, referred to as $\F_{C}^{D}$ in the manuscript
    p_face_idxs = np.copy(ear_p_face_idxs)

    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)

    # smoothing + quality control for the base layer in sacrum
    # neighbour info
    boundary_p_vertex_idxs, boundary_p_face_idxs, neigh_p_face_list = src.neighbouring_info(p_vertices,
                                                                                            p_faces[p_face_idxs])
    # measure dihedral angle
    max_angles_p = src.get_dihedral_angle(p_vertices, p_faces, p_face_idxs, neigh_p_face_list)
    max_angle_p = np.max(max_angles_p)
    max_angle_p = np.round(max_angle_p, 2)

    print("Primary side: max dihedral angle before smoothing is ", max_angle_p,
          "radians (", np.round(math.degrees(max_angle_p), 2), "degrees).")

    # norm visualization
    # centroids_p, end_points_p = src.norm_visualization(p_vertices, p_faces[p_face_idxs])
    # frame = mp.plot(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_p, end_points_p, shading={"line_color": "aqua"})

    # apply the smoothing + remove penetration/gap
    iteration = []

    for ss in range(param.smoothing_iteration_base):

        p_vertices = src.smooth_boundary(p_vertices, boundary_p_vertex_idxs, param.smoothing_factor)
        p_vertices = src.snap_to_surface(p_vertices, pb_vertices, p_faces)
        smoothed_max_angles_p = src.get_dihedral_angle(p_vertices,
                                                       p_faces,
                                                       p_face_idxs,
                                                       neigh_p_face_list)

        folded_p_vertex_idxs = []
        # np.float64(2) # max_angle
        for count, i in enumerate(smoothed_max_angles_p):
            if i > np.float64(2):
                folded_p_vertex_idxs.append(count)
                iteration.append(ss - 1)

    smoothed_max_angle_p = np.max(smoothed_max_angles_p)
    smoothed_max_angle_p = np.round(smoothed_max_angle_p, 2)

    print("Primary side: max dihedral angle after smoothing is ", smoothed_max_angle_p,
          "radians (", np.round(math.degrees(smoothed_max_angle_p), 2), "degrees).")
    print("")

    # norm visualization
    # centroids_p, end_points_p = src.norm_visualization(p_vertices, p_faces[p_face_idxs])
    # frame = mp.plot(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_p, end_points_p, shading={"line_color": "aqua"})

    print("Quality control results for the primary side: ")

    if len(folded_p_vertex_idxs) != 0:
        print("- There are issues with these vertex indices", folded_p_vertex_idxs)
        print("- Solution 1: To prevent this issue, decrease your 'param.smoothing_iteration' to ", iteration[0])
        print("- Solution 2: By default the faulty triangles will be removed from the face index list ")
        print("")

        # vz
        print("faulty vertices & neighbouring triangles:")
        frame = mp.plot(p_vertices, faces_p[p_face_idxs], c=src.pastel_blue, shading=src.sh_false)
        frame.add_points(p_vertices[boundary_p_vertex_idxs[folded_p_vertex_idxs]],
                         shading={"point_size": 0.2, "point_color": "red"})

        faces = p_faces[p_face_idxs]
        for i in folded_p_vertex_idxs:
            frame.add_mesh(p_vertices, faces[np.array(neigh_p_face_list[i])], c=src.sweet_pink,
                           shading=src.sh_true)
            frame.add_mesh(p_vertices, faces[np.array(boundary_p_face_idxs[i])], c=src.pastel_yellow,
                           shading=src.sh_true)

        if param.fix_boundary:
            p_face_idxs = src.fix_boundary(p_vertices, p_faces, p_face_idxs, boundary_p_vertex_idxs,
                                           folded_p_vertex_idxs)
            boundary_p_vertex_idxs = igl.boundary_loop(faces_p[p_face_idxs])

            # print("normal visualization of the fixed result:")
            # centroids_p, end_points_p = src.norm_visualization(p_vertices, p_faces[p_face_idxs])
            # frame = mp.plot(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)
            # frame.add_lines(centroids_p, end_points_p, shading={"line_color": "aqua"})

    else:
        print("Everything is clean in the primary interface. We will now continue to the secondary interface:")
        print("")

    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)

    ' Step B. Secondary interface definition in two versions, with and without gap in the hip joint'

    _, int_s_vertex_idxs = src.get_initial_surface2(p_vertices,
                                                    p_faces[p_face_idxs],
                                                    s_vertices,
                                                    s_faces,
                                                    param.gap_distance)

    int_s_face_idxs = []
    for j in int_s_vertex_idxs:
        for k in range(cumulative_sum_s[j], cumulative_sum_s[j + 1]):
            int_s_face_idxs += [face_adjacency_s[k]]

    int_s_face_idxs = np.array(int_s_face_idxs)

    rm_out_int_face_idxs_s = src.trim_boundary(s_faces,
                                               int_s_face_idxs,
                                               face_adjacency_s,
                                               cumulative_sum_s,
                                               1)

    if param.trimming_iteration_s != 0:
        trim_s_face_idxs = src.trim_boundary(s_faces,
                                             rm_out_int_face_idxs_s,
                                             face_adjacency_s,
                                             cumulative_sum_s,
                                             param.trimming_iteration_s)
    else:
        trim_s_face_idxs = np.copy(rm_out_int_face_idxs_s)

    one_s_face_idxs = src.get_largest_component(s_faces, trim_s_face_idxs)

    for i in range(10):
        one_s_face_idxs = src.remove_ears(s_faces, one_s_face_idxs)


    s_face_idxs = src.gap_fill(s_vertices, s_faces, one_s_face_idxs, face_adjacency_s, cumulative_sum_s)

    frame = mp.plot(s_vertices, s_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(s_vertices, s_faces[s_face_idxs], c=src.pastel_green, shading=src.sh_true)
    frame.add_points(s_vertices[int_s_vertex_idxs], shading={"point_size": 3, "point_color": "red"})

    # smoothing + quality control for the base layer for the secondary interface

    # neighbour info
    boundary_s_vertex_idxs, boundary_s_face_idxs, neigh_s_face_list = src.neighbouring_info(s_vertices,
                                                                                            s_faces[s_face_idxs])
    # measure dihedral angle
    max_angles_s = src.get_dihedral_angle(s_vertices, s_faces, s_face_idxs, neigh_s_face_list)
    max_angle_s = np.max(max_angles_s)
    max_angle_s = np.round(max_angle_s, 2)

    print("Secondary layer: max dihedral angle before smoothing is ", max_angle_s,
          "radians (", np.round(math.degrees(max_angle_s), 2), "degrees).")

    # norm visualization
    # centroids_s, end_points_s = src.norm_visualization(s_vertices, s_faces[s_face_idxs])
    # frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_s, end_points_s, shading={"line_color": "aqua"})

    # apply the smoothing + remove penetration/gap
    iteration = []

    for ss in range(param.smoothing_iteration_extruded_base):

        s_vertices = src.smooth_boundary(s_vertices, boundary_s_vertex_idxs, param.smoothing_factor)
        s_vertices = src.snap_to_surface(s_vertices, sb_vertices, s_faces)
        smoothed_max_angles_s = src.get_dihedral_angle(s_vertices, s_faces, s_face_idxs, neigh_s_face_list)

        folded_s_vertex_idxs = []
        # np.float64(2) # max_angle
        for count, i in enumerate(smoothed_max_angles_s):
            if i > np.float64(2):
                folded_s_vertex_idxs.append(count)
                iteration.append(ss - 1)

    smoothed_max_angle_secondary= np.max(smoothed_max_angles_s)
    smoothed_max_angle_secondary = np.round(smoothed_max_angle_secondary, 2)

    print("Secondary layer: max dihedral angle after smoothing is ", smoothed_max_angle_secondary,
          "radians (", np.round(math.degrees(smoothed_max_angle_secondary), 2), "degrees).")

    # norm visualization
    # centroids_s, end_points_s = src.norm_visualization(s_vertices, s_faces[s_face_idxs])
    # frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_s, end_points_s, shading={"line_color": "aqua"})

    print("Quality control results for the base layer: ")
    print("")
    if len(folded_s_vertex_idxs) != 0:
        print("- There are issues with these vertex indices", folded_s_vertex_idxs)
        print("- Solution 1: To prevent this issue, decrease your 'param.smoothing_iteration' to ", iteration[0])
        print("- Solution 2: By default the faulty triangles will be removed from the face index list ")
        print("")

        # vz
        print("faulty vertices & neighbouring triangles:")
        frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_yellow, shading=src.sh_false)
        frame.add_points(s_vertices[boundary_s_vertex_idxs[folded_s_vertex_idxs]],
                         shading={"point_size": 0.2, "point_color": "red"})

        faces = s_faces[s_face_idxs]
        for i in folded_vertex_idxs:
            frame.add_mesh(s_vertices, faces[np.array(neigh_s_face_list[i])], c=src.sweet_pink,
                           shading=src.sh_true)
            frame.add_mesh(s_vertices, faces[np.array(boundary_s_face_idxs[i])], c=src.pastel_yellow,
                           shading=src.sh_true)

        if param.fix_boundary:
            s_face_idxs = src.fix_boundary(s_vertices, s_faces, s_face_idxs, boundary_s_vertex_idxs,
                                           folded_s_vertex_idxs)
            boundary_s_vertex_idxs = igl.boundary_loop(s_faces[s_face_idxs])
            print("normal visualization of the fixed result:")
            # centroids_s, end_points_s = src.norm_visualization(s_vertices, s_faces[s_face_idxs])
            # frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_blue, shading=src.sh_true)
            # frame.add_lines(centroids_s, end_points_s, shading={"line_color": "aqua"})

    else:
        print("Everything is clean in the base layer. We will now continue to create the wall:")
        print("")

    frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_green, shading=src.sh_true)
    frame.add_mesh(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)

    " Step C. close the cartilage using the sweep-line technique, referred to as $faces_{C}^{R}$ in the manuscript"

    # flip normals of the bottom surface
    p_faces_flipped = p_faces[p_face_idxs]
    p_faces_flipped[:, [0, 1]] = p_faces_flipped[:, [1, 0]]

    s_faces_flipped = s_faces[s_face_idxs]
    s_faces_flipped[:, [0, 1]] = s_faces_flipped[:, [1, 0]]

    int_c_vertices, int_c_faces = src.get_wall_sweep(p_vertices, p_faces_flipped, s_vertices, s_faces_flipped)

    frame = mp.plot(s_vertices, s_faces_flipped, c=src.pastel_green, shading=src.sh_true)
    frame.add_mesh(p_vertices, p_faces_flipped, c=src.pastel_blue, shading=src.sh_true)
    frame.add_mesh(int_c_vertices, int_c_faces, c=src.sweet_pink, shading=src.sh_true)

    # merge the primary interface, secondary interface, and the closing surface
    int_sj_vertices = np.concatenate((p_vertices, int_c_vertices, s_vertices))
    int_sj_faces    = np.concatenate((p_faces_flipped, int_c_faces + len(p_vertices), s_faces_flipped + len(p_vertices) + len(int_c_vertices)))

    # increase the number of facet rows in the wall
    up_sj_vertices, up_sj_faces = igl.upsample(int_sj_vertices, int_sj_faces, param.upsampling_iteration)
    up_c_vertices, up_c_faces   = igl.upsample(int_c_vertices, int_c_faces, param.upsampling_iteration)

    # final touch
    sj_vertices, sj_faces = src.clean(up_sj_vertices, up_sj_faces)
    c_vertices, c_faces   = src.clean(up_c_vertices, up_c_faces)

    # centroids, end_points = src.norm_visualization(up_sj_vertices, up_sj_faces)
    # frame = mp.plot(up_sj_vertices, up_sj_faces, c=src.pastel_yellow, shading=src.sh_true)
    # frame.add_lines(centroids, end_points, shading={"line_color": "aqua"})

    frame = mp.plot(c_vertices, c_faces, c=src.sweet_pink, shading=src.sh_true)

    frame = mp.plot(sj_vertices, sj_faces, c=src.pastel_orange, shading=src.sh_true)
    frame.add_mesh(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(s_vertices, s_faces, c=src.bone, shading=src.sh_false)

    if param.full_model:
        output_vertices = sj_vertices
        output_faces = sj_faces
    else:
        output_vertices = c_vertices
        output_faces = c_faces

    " Step D. stats "

    df = pd.read_csv(str(anatomical_path), encoding='utf-8')

    # cartilage area
    cartilage_area_p = src.get_area(p_vertices, p_faces[p_face_idxs])
    cartilage_area_s = src.get_area(s_vertices, s_faces[s_face_idxs])

    # average thickness
    triangle_centroids = igl.barycenter(p_vertices, p_faces[p_face_idxs])
    sdd, _, _ = igl.signed_distance(triangle_centroids, s_vertices, s_faces[s_face_idxs], return_normals=False)
    sddd = np.round(np.mean(sdd), 2)


    if df.loc[18, 'Value'] == 'empty':
        df.loc[18, 'Value'] = np.round(cartilage_area_p, 2)
        df.loc[19, 'Value'] = np.round(cartilage_area_s, 2)
        df.loc[20, 'Value'] = sddd
    else:
        df.loc[21, 'Value'] = np.round(cartilage_area_p, 2)
        df.loc[22, 'Value'] = np.round(cartilage_area_s, 2)
        df.loc[23, 'Value'] = sddd

    # write to the specific anatomical file for each subject
    df.to_csv(str(anatomical_path), index=False)

    return p_vertices, s_vertices, output_vertices, output_faces


def get_gap_pj(pb_vertices, pb_faces, sb_vertices, sb_faces, param, anatomical_path ):

    """
    This function generates single-piece cartilage for the pubic joint

    :param pb_vertices: list of vertex positions of the primary bone
    :param pb_faces: list of triangle of the primary primary bone
    :param sb_vertices: list of vertex positions of the secondary bone
    :param sb_faces: list of triangle indices of the secondary bone
    :param param: list of parameters needed to generate the cartilage models located in the config folder
    :param anatomical_path: path to the joint anatomical measurements

    :return: vertices and faces of the pubic joint
    """

    # primary and secondary interface vertices and faces
    p_vertices = np.copy(pb_vertices)
    p_faces = np.copy(pb_faces)
    s_vertices = np.copy(sb_vertices)
    s_faces = np.copy(sb_faces)

    # bone adjacency faces
    face_adjacency_p, cumulative_sum_p = igl.vertex_triangle_adjacency(p_faces, len(p_vertices))
    face_adjacency_s, cumulative_sum_s = igl.vertex_triangle_adjacency(s_faces, len(s_vertices))

    " Step A. Primary interface estimation "

    # initial estimation
    int_p_face_idxs, _ = src.get_initial_surface(p_vertices, p_faces, sb_vertices, sb_faces, param.gap_distance)

    # trim the cartilage boundary layer
    if param.trimming_iteration_p != 0 :
        trim_p_face_idxs = src.trim_boundary(p_faces,
                                             int_p_face_idxs,
                                             face_adjacency_p,
                                             cumulative_sum_p,
                                             param.trimming_iteration_p)
    else:
        trim_p_face_idxs = np.copy(int_p_face_idxs)

    # removing extra components
    ear_p_face_idxs = src.get_largest_component(p_faces, trim_p_face_idxs)

    # remove ears
    ear_p_face_idxs = np.copy(ear_p_face_idxs)
    for i in range(10):
        ear_p_face_idxs = src.remove_ears(p_faces, ear_p_face_idxs)

    # the primary interface of the pubic joint, referred to as $\F_{C}^{D}$ in the manuscript
    p_face_idxs = np.copy(ear_p_face_idxs)

    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)

    # smoothing + quality control for the base layer in sacrum
    # neighbour info
    boundary_p_vertex_idxs, boundary_p_face_idxs, neigh_p_face_list = src.neighbouring_info(p_vertices,
                                                                                            p_faces[p_face_idxs])
    # measure dihedral angle
    max_angles_p = src.get_dihedral_angle(p_vertices, p_faces, p_face_idxs, neigh_p_face_list)
    max_angle_p = np.max(max_angles_p)
    max_angle_p = np.round(max_angle_p, 2)

    print("Primary side: max dihedral angle before smoothing is ", max_angle_p,
          "radians (", np.round(math.degrees(max_angle_p), 2), "degrees).")

    # norm visualization
    # centroids_p, end_points_p = src.norm_visualization(p_vertices, p_faces[p_face_idxs])
    # frame = mp.plot(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_p, end_points_p, shading={"line_color": "aqua"})

    # apply the smoothing + remove penetration/gap
    iteration = []

    for ss in range(param.smoothing_iteration_base):

        p_vertices = src.smooth_boundary(p_vertices, boundary_p_vertex_idxs, param.smoothing_factor)
        p_vertices = src.snap_to_surface(p_vertices, pb_vertices, p_faces)
        smoothed_max_angles_p = src.get_dihedral_angle(p_vertices,
                                                       p_faces,
                                                       p_face_idxs,
                                                       neigh_p_face_list)

        folded_p_vertex_idxs = []
        # np.float64(2) # max_angle
        for count, i in enumerate(smoothed_max_angles_p):
            if i > np.float64(2):
                folded_p_vertex_idxs.append(count)
                iteration.append(ss - 1)

    smoothed_max_angle_p = np.max(smoothed_max_angles_p)
    smoothed_max_angle_p = np.round(smoothed_max_angle_p, 2)

    print("Primary side: max dihedral angle after smoothing is ", smoothed_max_angle_p,
          "radians (", np.round(math.degrees(smoothed_max_angle_p), 2), "degrees).")
    print("")

    # norm visualization
    # centroids_p, end_points_p = src.norm_visualization(p_vertices, p_faces[p_face_idxs])
    # frame = mp.plot(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_p, end_points_p, shading={"line_color": "aqua"})

    print("Quality control results for the primary side: ")

    if len(folded_p_vertex_idxs) != 0:
        print("- There are issues with these vertex indices", folded_p_vertex_idxs)
        print("- Solution 1: To prevent this issue, decrease your 'param.smoothing_iteration' to ", iteration[0])
        print("- Solution 2: By default the faulty triangles will be removed from the face index list ")
        print("")

        # vz
        print("faulty vertices & neighbouring triangles:")
        frame = mp.plot(p_vertices, faces_p[p_face_idxs], c=src.pastel_blue, shading=src.sh_false)
        frame.add_points(p_vertices[boundary_p_vertex_idxs[folded_p_vertex_idxs]],
                         shading={"point_size": 0.2, "point_color": "red"})

        faces = p_faces[p_face_idxs]
        for i in folded_p_vertex_idxs:
            frame.add_mesh(p_vertices, faces[np.array(neigh_p_face_list[i])], c=src.sweet_pink,
                           shading=src.sh_true)
            frame.add_mesh(p_vertices, faces[np.array(boundary_p_face_idxs[i])], c=src.pastel_yellow,
                           shading=src.sh_true)

        if param.fix_boundary:
            p_face_idxs = src.fix_boundary(p_vertices, p_faces, p_face_idxs, boundary_p_vertex_idxs,
                                           folded_p_vertex_idxs)
            boundary_p_vertex_idxs = igl.boundary_loop(faces_p[p_face_idxs])

            # print("normal visualization of the fixed result:")
            # centroids_p, end_points_p = src.norm_visualization(p_vertices, p_faces[p_face_idxs])
            # frame = mp.plot(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)
            # frame.add_lines(centroids_p, end_points_p, shading={"line_color": "aqua"})

    else:
        print("Everything is clean in the primary interface. We will now continue to the secondary interface:")
        print("")

    frame = mp.plot(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)

    ' Step B. Secondary interface definition in two versions, with and without gap in the hip joint'

    # initial estimation
    int_s_face_idxs, _ = src.get_initial_surface(s_vertices, s_faces, pb_vertices, pb_faces, param.gap_distance)

    # trim
    if param.trimming_iteration_s != 0:
        trim_s_face_idxs = src.trim_boundary(s_faces,
                                             int_s_face_idxs,
                                             face_adjacency_s,
                                             cumulative_sum_s,
                                             param.trimming_iteration_s)
    else:
        trim_s_face_idxs = np.copy(int_s_face_idxs)

    # keep the largest piece
    one_s_face_idxs = src.get_largest_component(s_faces, trim_s_face_idxs)

    # remove ears
    for i in range(10):
        one_s_face_idxs = src.remove_ears(s_faces, one_s_face_idxs)


    s_face_idxs = np.copy (one_s_face_idxs)

    frame = mp.plot(s_vertices, s_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(s_vertices, s_faces[s_face_idxs], c=src.pastel_green, shading=src.sh_true)

    # smoothing + quality control for the base layer for the secondary interface

    # neighbour info
    boundary_s_vertex_idxs, boundary_s_face_idxs, neigh_s_face_list = src.neighbouring_info(s_vertices,
                                                                                            s_faces[s_face_idxs])
    # measure dihedral angle
    max_angles_s = src.get_dihedral_angle(s_vertices, s_faces, s_face_idxs, neigh_s_face_list)
    max_angle_s = np.max(max_angles_s)
    max_angle_s = np.round(max_angle_s, 2)

    print("Secondary layer: max dihedral angle before smoothing is ", max_angle_s,
          "radians (", np.round(math.degrees(max_angle_s), 2), "degrees).")

    # norm visualization
    # centroids_s, end_points_s = src.norm_visualization(s_vertices, s_faces[s_face_idxs])
    # frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_s, end_points_s, shading={"line_color": "aqua"})

    # apply the smoothing + remove penetration/gap
    iteration = []

    for ss in range(param.smoothing_iteration_extruded_base):

        s_vertices = src.smooth_boundary(s_vertices, boundary_s_vertex_idxs, param.smoothing_factor)
        s_vertices = src.snap_to_surface(s_vertices, sb_vertices, s_faces)
        smoothed_max_angles_s = src.get_dihedral_angle(s_vertices, s_faces, s_face_idxs, neigh_s_face_list)

        folded_s_vertex_idxs = []
        # np.float64(2) # max_angle
        for count, i in enumerate(smoothed_max_angles_s):
            if i > np.float64(2):
                folded_s_vertex_idxs.append(count)
                iteration.append(ss - 1)

    smoothed_max_angle_secondary= np.max(smoothed_max_angles_s)
    smoothed_max_angle_secondary = np.round(smoothed_max_angle_secondary, 2)

    print("Secondary layer: max dihedral angle after smoothing is ", smoothed_max_angle_secondary,
          "radians (", np.round(math.degrees(smoothed_max_angle_secondary), 2), "degrees).")

    # norm visualization
    # centroids_s, end_points_s = src.norm_visualization(s_vertices, s_faces[s_face_idxs])
    # frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_blue, shading=src.sh_true)
    # frame.add_lines(centroids_s, end_points_s, shading={"line_color": "aqua"})

    print("Quality control results for the base layer: ")
    print("")
    if len(folded_s_vertex_idxs) != 0:
        print("- There are issues with these vertex indices", folded_s_vertex_idxs)
        print("- Solution 1: To prevent this issue, decrease your 'param.smoothing_iteration' to ", iteration[0])
        print("- Solution 2: By default the faulty triangles will be removed from the face index list ")
        print("")

        # vz
        print("faulty vertices & neighbouring triangles:")
        frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_yellow, shading=src.sh_false)
        frame.add_points(s_vertices[boundary_s_vertex_idxs[folded_s_vertex_idxs]],
                         shading={"point_size": 0.2, "point_color": "red"})

        faces = s_faces[s_face_idxs]
        for i in folded_vertex_idxs:
            frame.add_mesh(s_vertices, faces[np.array(neigh_s_face_list[i])], c=src.sweet_pink,
                           shading=src.sh_true)
            frame.add_mesh(s_vertices, faces[np.array(boundary_s_face_idxs[i])], c=src.pastel_yellow,
                           shading=src.sh_true)

        if param.fix_boundary:
            s_face_idxs = src.fix_boundary(s_vertices, s_faces, s_face_idxs, boundary_s_vertex_idxs,
                                           folded_s_vertex_idxs)
            boundary_s_vertex_idxs = igl.boundary_loop(s_faces[s_face_idxs])
            print("normal visualization of the fixed result:")
            # centroids_s, end_points_s = src.norm_visualization(s_vertices, s_faces[s_face_idxs])
            # frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_blue, shading=src.sh_true)
            # frame.add_lines(centroids_s, end_points_s, shading={"line_color": "aqua"})

    else:
        print("Everything is clean in the base layer. We will now continue to create the wall:")

    frame = mp.plot(s_vertices, s_faces[s_face_idxs], c=src.pastel_green, shading=src.sh_true)
    frame.add_mesh(p_vertices, p_faces[p_face_idxs], c=src.pastel_blue, shading=src.sh_true)

    " Step C. close the cartilage using the sweep-line technique, referred to as $faces_{C}^{R}$ in the manuscript "

    # flip normals of the bottom surface
    p_faces_flipped = p_faces[p_face_idxs]
    p_faces_flipped[:, [0, 1]] = p_faces_flipped[:, [1, 0]]

    s_faces_flipped = s_faces[s_face_idxs]
    s_faces_flipped[:, [0, 1]] = s_faces_flipped[:, [1, 0]]

    int_c_vertices, int_c_faces = src.get_wall_sweep(p_vertices, p_faces_flipped, s_vertices, s_faces_flipped)

    frame = mp.plot(s_vertices, s_faces_flipped, c=src.pastel_green, shading=src.sh_true)
    frame.add_mesh(p_vertices, p_faces_flipped, c=src.pastel_blue, shading=src.sh_true)
    frame.add_mesh(int_c_vertices, int_c_faces, c=src.sweet_pink, shading=src.sh_true)

    # merge the primary interface, secondary interface, and the closing surface
    int_sj_vertices = np.concatenate((p_vertices, int_c_vertices, s_vertices))
    int_sj_faces    = np.concatenate((p_faces_flipped, int_c_faces + len(p_vertices), s_faces_flipped + len(p_vertices) + len(int_c_vertices)))

    # increase the number of facet rows in the wall
    up_sj_vertices, up_sj_faces = igl.upsample(int_sj_vertices, int_sj_faces, param.upsampling_iteration)
    up_c_vertices, up_c_faces   = igl.upsample(int_c_vertices, int_c_faces, param.upsampling_iteration)

    # final touch
    sj_vertices, sj_faces = src.clean(up_sj_vertices, up_sj_faces)
    c_vertices, c_faces   = src.clean(up_c_vertices, up_c_faces)

    # centroids, end_points = src.norm_visualization(up_sj_vertices, up_sj_faces)
    # frame = mp.plot(up_sj_vertices, up_sj_faces, c=src.pastel_yellow, shading=src.sh_true)
    # frame.add_lines(centroids, end_points, shading={"line_color": "aqua"})

    mp.plot(c_vertices, c_faces, c=src.sweet_pink, shading=src.sh_true)

    frame = mp.plot(sj_vertices, sj_faces, c=src.pastel_orange, shading=src.sh_true)
    frame.add_mesh(p_vertices, p_faces, c=src.bone, shading=src.sh_false)
    frame.add_mesh(s_vertices, s_faces, c=src.bone, shading=src.sh_false)

    if param.full_model:
        output_vertices = sj_vertices
        output_faces = sj_faces
    else:
        output_vertices = c_vertices
        output_faces = c_faces

    " Step D. stats "

    df = pd.read_csv(str(anatomical_path), encoding='utf-8')

    # cartilage area
    cartilage_area_p = src.get_area(p_vertices, p_faces[p_face_idxs])
    cartilage_area_s = src.get_area(s_vertices, s_faces[s_face_idxs])

    # average thickness
    triangle_centroids = igl.barycenter(p_vertices, p_faces[p_face_idxs])
    sdd, _, _ = igl.signed_distance(triangle_centroids, s_vertices, s_faces[s_face_idxs], return_normals=False)
    sddd = np.round(np.mean(sdd), 2)

    df.loc[24, 'Value'] = np.round(cartilage_area_p, 2)
    df.loc[25, 'Value'] = np.round(cartilage_area_s, 2)
    df.loc[26, 'Value'] = sddd

    # write to the specific anatomical file for each subject
    df.to_csv(str(anatomical_path), index=False)

    return p_vertices, s_vertices, output_vertices, output_faces
