import json
import os
import meshio
import numpy as np
import src
from pathlib import Path
import meshplot as mp
import igl
import matplotlib.pyplot as plt


def mk_union(left, right):
    """

    :param left:
    :param right:
    :return:
    """
    return dict(operation='union', left=left, right=right)


def mk_diff(left, right):
    """

    :param left:
    :param right:
    :return:
    """
    return dict(operation='difference', left=left, right=right)


def mk_intersect(left, right):
    """

    :param left:
    :param right:
    :return:
    """
    return dict(operation='intersection', left=left, right=right)


def mk_json(name, operation, json_dir):
    """

    :param name:
    :param operation:
    :param json_dir:
    :return:
    """

    prev_path = Path.cwd()

    os.chdir(json_dir)

    with open(name + ".json", 'w') as json_file:
        json.dump(operation, json_file)

    os.chdir(prev_path)

    # json_path = str(json_dir/name) + ".json"
    json_path = (json_dir / name).with_suffix('.json')

    return json_path


def run_boolean(ftetwild_dir, json_path, output_path, epsilon, edge_length):
    """
    :param ftetwild_dir: locate this path to the 'build' folder of ftetwild.
    :param json_path:
    :param output_path:
    :param epsilon:
    :param edge_length:

    """


    json_path = str(json_path.resolve())

    prev_path = Path.cwd()

    os.chdir(ftetwild_dir)
    os.system("./FloatTetwild_bin --csg " + json_path +
              " --level 3 -e " + epsilon + " -l " + edge_length +
              " -o " + output_path + " --no-binary --no-color --export-raw")

    os.chdir(prev_path)
#--stop-energy 8

def viz(vertices, elements, tet_physical):
    """

    :param vertices:
    :param elements:
    :param tet_physical:
    :return:
    """

    # all the nodes
    # frame = mp.plot(vertices, shading={"point_size": 0.5, "point_color": "red"})

    # result
    mp.plot(vertices, elements, c=src.pastel_blue, shading=src.sh_true)

    # separated results
    idxs = np.where(tet_physical[0] == 1)
    idxss = np.where(tet_physical[0] == 2)

    frame2 = mp.plot(vertices, elements[idxs], c=src.pastel_green, shading=src.sh_true)
    frame2.add_mesh(vertices, elements[idxss], c=src.pastel_orange, shading=src.sh_true)

    # cut plane
    idx = make_cut_plane_view(vertices, elements, d=0, s=0.5)
    frame3 = mp.plot(vertices, elements[idx[0], :], c=src.pastel_green, shading=src.sh_true)

    q = elements[idxss]
    idxx = make_cut_plane_view(vertices, q, d=0, s=0.5)
    frame3.add_mesh(vertices, q[idxx[0], :], c=src.pastel_orange, shading=src.sh_true)

    # separate
    frame4 = mp.plot(vertices, elements[idxs], c=src.pastel_green, shading=src.sh_true)
    frame5 = mp.plot(vertices, elements[idxss], c=src.pastel_orange, shading=src.sh_true)


def make_cut_plane_view(v, f, d=0, s=0.5):
    """

    :param v:
    :param f:
    :param d:
    :param s:
    :return:
    """

    # d is the direction of the cut: x=0, y=1, z=2
    # s it the size of the cut where 1 is equal to no cut and 0 removes the whole object.

    a = np.amin(v, axis=0)
    print(a)
    b = np.amax(v, axis=0)
    h = s * (b - a) + a
    print(h)
    c = igl.barycenter(v, f)

    if d == 0:
        idx = np.where(c[:, 1] < h[1])
    elif d == 1:
        idx = np.where(c[:, 0] < h[0])
    else:
        idx = np.where(c[:, 2] < h[2])

    return idx

def read_volume_mesh(path, input_dimension, output_dimension):
    """

    :param path:
    :return:
    """

    mesh = meshio.read(path, file_format="gmsh")
    vertices = mesh.points
    elements = mesh.get_cells_type("tetra")

    if output_dimension == "m":
        vertices = vertices / 1000

    # print("number of elements:", len(elements))

    # tet_physical = mesh.cell_data["gmsh:physical"]
    # domains = np.unique(tet_physical[0])

    # print("the model has this many parts:", domains)

    return vertices, elements

def leg_filter (csg_output_dir, output_path, data_path,  vertices_c, faces_c, vertices_f, faces_f, input_dimension, output_dimension):

    raw_vertices, raw_elements = read_volume_mesh(csg_output_dir + "__all.msh", input_dimension, output_dimension)

    # barycenter
    barycenter = igl.barycenter(raw_vertices, raw_elements)

    # use signed distance to find cartilage tissue
    sd_c, _, _ = igl.signed_distance(barycenter, vertices_c, faces_c, return_normals=False)
    elemC_idxs = np.where(sd_c <= 0)[0]

    # winding number to find the femur bone
    wn_f = igl.fast_winding_number_for_meshes(vertices_f, faces_f, barycenter)

    # filter based on winding number
    elemF_idxs = np.where(wn_f > 0.1)[0]

    # alternative
    # sd_f, _, _ = igl.signed_distance(barycenter, vertices_f, faces_f, return_normals = False)
    # elemF_idxs =np.where(sd_f<=0)[0]

    # give priority to cartilage comparing to the femur bone
    _, _, mutualF_idxs = np.intersect1d(elemC_idxs, elemF_idxs, return_indices=True)
    elemF_idxs = np.delete(elemF_idxs, mutualF_idxs, axis=0)

    # viz together
    frame = mp.plot(raw_vertices, raw_elements[elemC_idxs], c=src.pastel_orange, shading=src.sh_true)
    frame.add_mesh(raw_vertices, raw_elements[elemF_idxs], c=src.bone, shading=src.sh_true)

    # merge elements
    merged_element_idxs = np.concatenate((elemC_idxs, elemF_idxs))

    # remove unreferenced
    physical_vertices, physical_elements, _, _ = igl.remove_unreferenced(raw_vertices,
                                                                         raw_elements[merged_element_idxs])

    # extract the model surface
    all_tri = igl.boundary_facets(physical_elements)

    all_tri_idxs = np.array(list(range(0, len(all_tri))))

    # flip the normals
    flipped_all_tri = np.copy(all_tri)
    flipped_all_tri[:, [0, 1]] = flipped_all_tri[:, [1, 0]]

    # femur surface
    femur_tri = igl.boundary_facets(physical_elements[len(elemC_idxs):])

    # flip the normals
    flipped_femur_tri = np.copy(femur_tri)
    flipped_femur_tri[:, [0, 1]] = flipped_femur_tri[:, [1, 0]]

    np.save(data_path + '_femur_faces', flipped_femur_tri )

    femur_tri_idxs = []

    for i in range(len(flipped_femur_tri)):
        ind = np.where(flipped_all_tri == flipped_femur_tri[i])[0]
        m = np.unique(ind, return_counts=True)[1]
        o = np.where(m == 3)[0]
        if len(o) != 0:
            femur_tri_idxs.append(ind[o[0]])

    slide_tri_idxs = np.delete(all_tri_idxs, femur_tri_idxs, axis=0)

    frame = mp.plot(physical_vertices, flipped_all_tri[slide_tri_idxs], c=src.pastel_blue, shading=src.sh_true)
    slide_surface_list = flipped_all_tri[slide_tri_idxs]

    np.save( data_path+'_sliding_faces', slide_surface_list )

    # cartilage surface
    cart_tri = igl.boundary_facets(physical_elements[:len(elemC_idxs)])

    # flip the normals
    flipped_cart_tri = np.copy(cart_tri)
    flipped_cart_tri[:, [0, 1]] = flipped_cart_tri[:, [1, 0]]

    # put labels in this new stack
    labels = np.zeros (len(physical_elements), dtype=int)
    labels[:len(elemC_idxs)] = 1
    labels[len(elemC_idxs):] = 2

    print('number of physical elements',np.unique(labels))
    print('length of elements 1', len(elemC_idxs))
    print('length of elements 2', len(elemF_idxs))
    print('length of labels', len(labels))

    # save
    if output_dimension == "m":
        physical_vertices = physical_vertices / 1000

    meshio.write_points_cells(
        output_path + '.msh',
        points=physical_vertices,
        cells=[("tetra", physical_elements)],
        cell_data={"gmsh:physical": np.array([labels]), "gmsh:geometrical": np.array([labels])},
        file_format="gmsh22",
        binary=False,
    )

    mylist = [len(elemC_idxs), len(elemF_idxs) ]
    np.save( data_path + '_element_idxs_list', mylist )

    # save the surface mesh of the femur
    f_vertices, f_faces, _, _ = igl.remove_unreferenced(physical_vertices, flipped_femur_tri)
    fc_vertices, fc_faces, _, _ = igl.remove_unreferenced(physical_vertices, flipped_cart_tri)

    igl.write_triangle_mesh( output_path + '_bn_femur.obj', f_vertices, f_faces)
    igl.write_triangle_mesh( output_path + '_jnt_fc.obj', fc_vertices, fc_faces)


def girdle_filter (csg_output_dir, output_path, data_path,  vertices_1, faces_1, vertices_2, faces_2, vertices_3, faces_3, vertices_4, faces_4,
                  vertices_5, faces_5, vertices_6, faces_6, vertices_7, faces_7, vertices_8, faces_8, input_dimension, output_dimension ):

    raw_vertices, raw_elements = read_volume_mesh(csg_output_dir +"__all.msh", input_dimension, output_dimension)

    # barycenter
    barycenter = igl.barycenter(raw_vertices, raw_elements)

    # use signed distance to find "lsi"
    sd_1, _, _ = igl.signed_distance(barycenter, vertices_1, faces_1, return_normals=False)
    elem_idxs_1 = np.where(sd_1 <= 0)[0]

    # wn for the surface meshes
    # wn_1 = igl.fast_winding_number_for_meshes(vertices_1, faces_1, barycenter)
    #
    # plt.hist(wn_1, 50)
    # plt.show()

    # # filter based on winding number
    # elem_idxs_1 = np.where(wn_1 >0.08)[0]

    # viz together
    # frame = mp.plot(raw_vertices, raw_elements[elem_idxs_1], c=src.pastel_orange, shading=src.sh_true)
    # frame.add_mesh(vertices_1, faces_1, c = src.bone, shading = src.sh_true)

    # use signed distance to find "rsi"
    sd_2, _, _ = igl.signed_distance(barycenter, vertices_2, faces_2, return_normals = False)
    elem_idxs_2 =np.where(sd_2<=0)[0]

    # use signed distance to find "lpc"
    sd_3, _, _ = igl.signed_distance(barycenter, vertices_3, faces_3, return_normals=False)
    elem_idxs_3 = np.where(sd_3 <= 0)[0]

    # use signed distance to find "rpc"
    sd_4, _, _ = igl.signed_distance(barycenter, vertices_4, faces_4, return_normals=False)
    elem_idxs_4 = np.where(sd_4 <= 0)[0]

    # use signed distance to find "pubic"
    sd_5, _, _ = igl.signed_distance(barycenter, vertices_5, faces_5, return_normals=False)
    elem_idxs_5 = np.where(sd_5 <= 0)[0]

    # use signed distance to find "sacrum"
    sd_6, _, _ = igl.signed_distance(barycenter, vertices_6, faces_6, return_normals=False)
    elem_idxs_6 = np.where(sd_6 <= 0)[0]

    # use signed distance to find "lpelvis"
    sd_7, _, _ = igl.signed_distance(barycenter, vertices_7, faces_7, return_normals=False)
    elem_idxs_7 = np.where(sd_7 <= 0)[0]

    # use signed distance to find "rpelvis"
    sd_8, _, _ = igl.signed_distance(barycenter, vertices_8, faces_8, return_normals=False)
    elem_idxs_8 = np.where(sd_8 <= 0)[0]


    # give priority to cartilage comparing to bone (first is always cartilage)

    # lsi and sacrum
    _, _, mutual_ind_6 = np.intersect1d(elem_idxs_1, elem_idxs_6, return_indices=True)
    elem_idxs_6 = np.delete(elem_idxs_6, mutual_ind_6, axis=0)

    # lsi and lpelvis
    _, _, mutual_ind_7 = np.intersect1d(elem_idxs_1, elem_idxs_7, return_indices=True)
    elem_idxs_7 = np.delete(elem_idxs_7, mutual_ind_7, axis=0)

    # rsi and sacrum
    _, _, mutual_ind_6 = np.intersect1d(elem_idxs_2, elem_idxs_6, return_indices=True)
    elem_idxs_6 = np.delete(elem_idxs_6, mutual_ind_6, axis=0)

    # rsi and rpelvis
    _, _, mutual_ind_8 = np.intersect1d(elem_idxs_2, elem_idxs_8, return_indices=True)
    elem_idxs_8 = np.delete(elem_idxs_8, mutual_ind_8, axis=0)

    # lpc and lpelvis
    _, _, mutual_ind_7 = np.intersect1d(elem_idxs_3, elem_idxs_7, return_indices=True)
    elem_idxs_7 = np.delete(elem_idxs_7, mutual_ind_7, axis=0)

    # rpc and rpelvis
    _, _, mutual_ind_8 = np.intersect1d(elem_idxs_4, elem_idxs_8, return_indices=True)
    elem_idxs_8 = np.delete(elem_idxs_8, mutual_ind_8, axis=0)

    # pubic and lpelvis
    _, _, mutual_ind_7 = np.intersect1d(elem_idxs_5, elem_idxs_7, return_indices=True)
    elem_idxs_7 = np.delete(elem_idxs_7, mutual_ind_7, axis=0)

    # pubic and rpelvis
    _, _, mutual_ind_8 = np.intersect1d(elem_idxs_5, elem_idxs_8, return_indices=True)
    elem_idxs_8 = np.delete(elem_idxs_8, mutual_ind_8, axis=0)

    # merge elements
    merged_element_idxs = np.concatenate((elem_idxs_1, elem_idxs_2,elem_idxs_3,elem_idxs_4,elem_idxs_5,elem_idxs_6,elem_idxs_7,elem_idxs_8 ))

    one = len(elem_idxs_1)
    two = len(elem_idxs_2)
    three = len(elem_idxs_3)
    four = len(elem_idxs_4)
    five = len(elem_idxs_5)
    six = len(elem_idxs_6)
    seven = len(elem_idxs_7)
    eight = len(elem_idxs_8)

    mylist = [one, two, three, four, five, six, seven, eight ]
    np.save(data_path + '_element_idxs_list', mylist)

    # remove unreferenced
    physical_vertices, physical_elements, _, _ = igl.remove_unreferenced(raw_vertices,
                                                                         raw_elements[merged_element_idxs])

    # put labels in this new stack
    labels = np.zeros(len(physical_elements), dtype=int)
    #lsi
    labels[:one] = 1
    #rsi
    labels[one:one+two] = 2
    # lpc
    labels[one+two:one+two+three] = 3
    # rpc
    labels[one+two+three:one+two+three+four] = 4
    # pubic
    labels[one+two+three+four:one+two+three+four+five] = 5
    # sacrum
    labels[one+two+three+four+five:one+two+three+four+five+six] = 6
    # lpelvis
    labels[one+two+three+four+five+six:one+two+three+four+five+six+seven] = 7
    # rpelvis
    labels[one+two+three+four+five+six+seven:] = 8

    print(np.unique(labels))

    print('length of elements one', one)
    print('length of elements two', two)
    print('length of elements three', three)
    print('length of elements four', four)
    print('length of elements five', five)
    print('length of elements six', six)
    print('length of elements seven', seven)
    print('length of elements eight', eight)

    print('length of labels', len(labels))
    #

    # extract the left master surface
    all_tri = igl.boundary_facets(physical_elements)
    all_tri_idxs = np.array(list(range(0, len(all_tri))))

    # flip the normals
    flipped_all_tri = np.copy(all_tri)
    flipped_all_tri[:, [0, 1]] = flipped_all_tri[:, [1, 0]]

    # rest surface
    lrest_elem_idxs = np.where(labels!=3)
    rrest_elem_idxs = np.where(labels != 4)

    lrest_tri = igl.boundary_facets(physical_elements[lrest_elem_idxs])
    rrest_tri = igl.boundary_facets(physical_elements[rrest_elem_idxs])

    # flip the normals
    flipped_lrest_tri = np.copy(lrest_tri)
    flipped_lrest_tri[:, [0, 1]] = flipped_lrest_tri[:, [1, 0]]

    flipped_rrest_tri = np.copy(rrest_tri)
    flipped_rrest_tri[:, [0, 1]] = flipped_rrest_tri[:, [1, 0]]

    lrest_tri_idxs = []
    for i in range(len(flipped_lrest_tri)):
        ind = np.where(flipped_all_tri == flipped_lrest_tri[i])[0]
        m = np.unique(ind, return_counts=True)[1]
        o = np.where(m == 3)[0]
        if len(o) != 0:
            lrest_tri_idxs.append(ind[o[0]])

    rrest_tri_idxs = []
    for i in range(len(flipped_rrest_tri)):
        ind = np.where(flipped_all_tri == flipped_rrest_tri[i])[0]
        m = np.unique(ind, return_counts=True)[1]
        o = np.where(m == 3)[0]
        if len(o) != 0:
            rrest_tri_idxs.append(ind[o[0]])

    lslide_tri_idxs = np.delete(all_tri_idxs, lrest_tri_idxs, axis=0)
    rslide_tri_idxs = np.delete(all_tri_idxs, rrest_tri_idxs, axis=0)

    frame = mp.plot(physical_vertices, flipped_all_tri[lslide_tri_idxs], c=src.pastel_blue, shading=src.sh_true)
    frame.add_mesh (physical_vertices, flipped_all_tri[rslide_tri_idxs], c=src.pastel_blue, shading=src.sh_true)

    lslide_surface_list = flipped_all_tri[lslide_tri_idxs]
    rslide_surface_list = flipped_all_tri[rslide_tri_idxs]

    np.save(data_path +'_lsliding_faces', lslide_surface_list)
    np.save(data_path +'_rsliding_faces', rslide_surface_list)

    # save each parts surface
    lsi_elem_idxs = np.where(labels == 1)
    rsi_elem_idxs = np.where(labels == 2)
    lpc_elem_idxs = np.where(labels == 3)
    rpc_elem_idxs = np.where(labels == 4)
    pubic_elem_idxs = np.where(labels == 5)
    sacrum_elem_idxs = np.where(labels == 6)
    lpelvis_elem_idxs = np.where(labels == 7)
    rpelvis_elem_idxs = np.where(labels == 8)


    lsi_tri = igl.boundary_facets(physical_elements[lsi_elem_idxs])
    rsi_tri = igl.boundary_facets(physical_elements[rsi_elem_idxs])
    lpc_tri = igl.boundary_facets(physical_elements[lpc_elem_idxs])
    rpc_tri = igl.boundary_facets(physical_elements[rpc_elem_idxs])
    pubic_tri = igl.boundary_facets(physical_elements[pubic_elem_idxs])
    sacrum_tri = igl.boundary_facets(physical_elements[sacrum_elem_idxs])
    lpelvis_tri = igl.boundary_facets(physical_elements[lpelvis_elem_idxs])
    rpelvis_tri = igl.boundary_facets(physical_elements[rpelvis_elem_idxs])

    # flip the normals
    flipped_lsi_tri = np.copy(lsi_tri)
    flipped_rsi_tri = np.copy(rsi_tri)
    flipped_lpc_tri = np.copy(lpc_tri)
    flipped_rpc_tri = np.copy(rpc_tri)
    flipped_pubic_tri = np.copy(pubic_tri)
    flipped_sacrum_tri = np.copy(sacrum_tri)
    flipped_lpelvis_tri = np.copy(lpelvis_tri)
    flipped_rpelvis_tri = np.copy(rpelvis_tri)

    flipped_lsi_tri[:, [0, 1]] = flipped_lsi_tri[:, [1, 0]]
    flipped_rsi_tri[:, [0, 1]] = flipped_rsi_tri[:, [1, 0]]
    flipped_lpc_tri[:, [0, 1]] = flipped_lpc_tri[:, [1, 0]]
    flipped_rpc_tri[:, [0, 1]] = flipped_rpc_tri[:, [1, 0]]
    flipped_pubic_tri[:, [0, 1]] = flipped_pubic_tri[:, [1, 0]]
    flipped_sacrum_tri[:, [0, 1]] = flipped_sacrum_tri[:, [1, 0]]
    flipped_lpelvis_tri[:, [0, 1]] = flipped_lpelvis_tri[:, [1, 0]]
    flipped_rpelvis_tri[:, [0, 1]] = flipped_rpelvis_tri[:, [1, 0]]


    # save
    if output_dimension == "m":
        physical_vertices = physical_vertices / 1000

    meshio.write_points_cells(
        output_path + '.msh',
        points=physical_vertices,
        cells=[("tetra", physical_elements)],
        cell_data={"gmsh:physical": np.array([labels]), "gmsh:geometrical": np.array([labels])},
        file_format="gmsh22",
        binary=False,
    )

    lsi_vertices, lsi_faces, _, _ = igl.remove_unreferenced(physical_vertices, flipped_lsi_tri)
    rsi_vertices, rsi_faces, _, _ = igl.remove_unreferenced(physical_vertices, flipped_rsi_tri)
    lpc_vertices, lpc_faces, _, _ = igl.remove_unreferenced(physical_vertices, flipped_lpc_tri)
    rpc_vertices, rpc_faces, _, _ = igl.remove_unreferenced(physical_vertices, flipped_rpc_tri)
    p_vertices,   p_faces,   _, _ = igl.remove_unreferenced(physical_vertices, flipped_pubic_tri)
    s_vertices,   s_faces,   _, _ = igl.remove_unreferenced(physical_vertices, flipped_sacrum_tri)
    lp_vertices,  lp_faces,  _, _ = igl.remove_unreferenced(physical_vertices, flipped_lpelvis_tri)
    rp_vertices,  rp_faces,  _, _ = igl.remove_unreferenced(physical_vertices, flipped_rpelvis_tri)

    igl.write_triangle_mesh(output_path + '_jnt_lsi.obj', lsi_vertices, lsi_faces)
    igl.write_triangle_mesh(output_path + '_jnt_rsi.obj', rsi_vertices, rsi_faces)
    igl.write_triangle_mesh(output_path + '_jnt_lac.obj', lpc_vertices, lpc_faces)
    igl.write_triangle_mesh(output_path + '_jnt_rac.obj', rpc_vertices, rpc_faces)
    igl.write_triangle_mesh(output_path + '_jnt_ps.obj', p_vertices,   p_faces)
    igl.write_triangle_mesh(output_path + '_bn_sacrum.obj',  s_vertices, s_faces)
    igl.write_triangle_mesh(output_path + '_bn_lpelvis.obj', lp_vertices,  lp_faces)
    igl.write_triangle_mesh(output_path + '_bn_rpelvis.obj', rp_vertices,  rp_faces)

    s_face_idxs = []
    for i in range(len(flipped_sacrum_tri)):
        ind = np.where(flipped_all_tri == flipped_sacrum_tri[i])[0]
        m = np.unique(ind, return_counts=True)[1]
        o = np.where(m == 3)[0]
        if len(o) != 0:
            s_face_idxs.append(ind[o[0]])

    wo_inner_surface_list = flipped_all_tri[s_face_idxs]
    np.save(data_path + '_sacrum_minus_sharing_interfaces', wo_inner_surface_list)


def merge_volume_mesh(vertices_1,
                       elements_1,
                       vertices_2,
                       elements_2):
    """
    Merges two surface meshes into one

    :param vertices_1: list of vertex positions of the first surface
    :param faces_1: list of faces of the first surface
    :param vertices_2: list of vertex positions of the second surface
    :param faces_2: list of faces of the second surface

    :return: The merged vertices and surfaces of the mesh
    """
    merged_vertices = np.concatenate((vertices_1, vertices_2))
    merged_elements = np.concatenate((elements_1, elements_2 + len(vertices_1)))

    return merged_vertices, merged_elements