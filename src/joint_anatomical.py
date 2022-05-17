import



" Sacroiliac Joint"

# average thickness

# primary bone coverage area

# secondary bone coverage area

" Pubic Joint"

# average thickness

# primary bone coverage area

# secondary bone coverage area


s_vertices, s_faces = src.fit_sphere_femur(vertices_p[base_vertex_idxs])

frame = mp.plot(vertices_p, faces_p, c=src.bone, shading=src.sh_false)
frame.add_mesh(s_vertices, s_faces, c=src.sweet_pink, shading=src.sh_true)



# # intialise data of lists.
    # lfc_data = {'Parameters': ['left HJ min joint space', 'Right HJ min joint space',
    #                            'lpc mean thickness', 'rpc mean thickness',
    #                            'lpc bone coverage area', 'rpc bone coverage area',
    #                            'lfc mean thickness', 'rfc mean thickness',
    #                            'lfc bone coverage area', 'rfc bone coverage area',
    #                            'minimum gap in left HJ', 'minimum gap in right HJ'
    #                            ],
    #             subject_id: [np.round(l, 2), np.round(lih, 2), np.round(rih, 2),
    #                          np.round(liw, 2), np.round(riw, 2), np.round(pw, 2),
    #                          np.round(lball_c, 2), np.round(rball_c, 2), np.round(lball_r, 2), np.round(rball_r, 2),
    #                          np.round(lfh_c, 2), np.round(rfh_c, 2), np.round(lmean_dist), np.round(rmean_dist),
    #                          np.round(ldist, 2), np.round(rdist, 2)
    #
    #                          ]}
    #
    # # Print the output.
    # print(lfc_df)
    #
    # # Create DataFrame'
    # param_output = '.csv'
    #
    # lfc_dfn = subject_id + '_lfc_df'
    # path = str((morpho_dir / lfc_dfn).with_suffix(param_output))
    #
    # lfc_df = pd.DataFrame(lfc_data)
    # lfc_df.to_csv(path)
