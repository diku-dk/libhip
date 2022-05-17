def nord_filter (csg_output_dir, output_path,
                 vertices_1, faces_1,
                 vertices_2, faces_2,
                 vertices_3, faces_3,
                 vertices_4, faces_4,
                 vertices_5, faces_5,
                 vertices_6, faces_6,
                 vertices_7, faces_7,
                 vertices_8, faces_8 ):
    """
    :param csg_output_dir: path to where the fTetWild raw output mesh is located (normally has a __all.msh format)
    :param output_path: Path where we want the partitioned .msh file to be saved as
    :param vertices_1, faces_1: surface mesh of the left sacroiliac cartilage (.obj )
    :param vertices_2, faces_2: surface mesh of the right sacroiliac cartilage  (.obj )
    :param vertices_3, faces_3: surface mesh of the left pelvic cartilage (.obj )
    :param vertices_4, faces_4: surface mesh of the right pelvic cartilage (.obj )
    :param vertices_5, faces_5: surface mesh of the pubic cartilage (.obj )
    :param vertices_6, faces_6: surface mesh of the sacrum bone (.obj )
    :param vertices_7, faces_7: surface mesh of the left pelvis bone (.obj )
    :param vertices_8, faces_8: surface mesh of the right pelvis bone (.obj )

    """

    raw_vertices, raw_elements = read_volume_mesh(csg_output_dir + "__all.msh")

    # barycenter
    barycenter = igl.barycenter(raw_vertices, raw_elements)

    # use signed distance to find "lsi"
    sd_1, _, _ = igl.signed_distance(barycenter, vertices_1, faces_1, return_normals=False)
    elem_idxs_1 = np.where(sd_1 <= 0)[0]


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
    merged_element_idxs = np.concatenate((elem_idxs_1, elem_idxs_2,
                                          elem_idxs_3,elem_idxs_4,
                                          elem_idxs_5,elem_idxs_6,
                                          elem_idxs_7,elem_idxs_8 ))

    one = len(elem_idxs_1)
    two = len(elem_idxs_2)
    three = len(elem_idxs_3)
    four = len(elem_idxs_4)
    five = len(elem_idxs_5)
    six = len(elem_idxs_6)
    seven = len(elem_idxs_7)
    eight = len(elem_idxs_8)

    mylist = [one, two, three, four, five, six, seven, eight ]
    np.save(output_path + '_element_idxs_list', mylist)

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

    # save volume
    meshio.write_points_cells(
        output_path + '.msh',
        points=physical_vertices,
        cells=[("tetra", physical_elements)],
        cell_data={"gmsh:physical": np.array([labels]), "gmsh:geometrical": np.array([labels])},
        file_format="gmsh22",
        binary=False,
    )

    # save each part as a separate surface
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

    igl.write_triangle_mesh(output_path + '_lsi.obj', physical_vertices, flipped_lsi_tri)
    igl.write_triangle_mesh(output_path + '_rsi.obj', physical_vertices, flipped_rsi_tri)
    igl.write_triangle_mesh(output_path + '_lpc.obj', physical_vertices, flipped_lpc_tri)
    igl.write_triangle_mesh(output_path + '_rpc.obj', physical_vertices, flipped_rpc_tri)
    igl.write_triangle_mesh(output_path + '_pubic.obj', physical_vertices, flipped_pubic_tri)
    igl.write_triangle_mesh(output_path + '_sacrum.obj', physical_vertices, flipped_sacrum_tri)
    igl.write_triangle_mesh(output_path + '_lpelvis.obj', physical_vertices, flipped_lpelvis_tri)
    igl.write_triangle_mesh(output_path + '_rpelvis.obj', physical_vertices, flipped_rpelvis_tri)