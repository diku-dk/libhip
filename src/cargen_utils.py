import numpy as np
import igl
import meshplot as mp
import matplotlib.pyplot as plt
import math
import wildmeshing as wm
import sys


def clean(vertices, faces):

    """
    this function removes duplicated faces and removes unreferenced vertices from the input mesh

    :param vertices: list of vertex positions
    :param faces: list of triangle indices

    :return: cleaned vertices and faces
    """
    # epsilon:  minimal distance to consider two vertices identical
    epsilon = np.min(igl.edge_lengths(vertices, faces)) / 100
    vertices, faces, _ = igl.remove_duplicates(vertices, faces, epsilon)
    faces, _ = igl.resolve_duplicated_faces(faces)
    vertices, faces, _, _ = igl.remove_unreferenced(vertices, faces)

    return vertices, faces


def read (path, input_dimension):

    """
    this function reads vertex and face information from an input surface mesh

    :param path: a path where the surface meshes are stored in
    :param input_dimension: the dimension of the input mesh ("mm" = millimeters, "m" = meters)

    :return: the vertices and faces corresponding to the input mesh
    """

    vertices, faces = igl.read_triangle_mesh(path, 'float')

    if input_dimension == "m":
        vertices = vertices * 1000

    print("number of faces after reading", len(faces))

    return vertices, faces


def read_and_clean(path, input_dimension):

    """
    this function reads vertex and face information from an input surface mesh

    :param path: a path where the surface meshes are stored in
    :param input_dimension: the dimension of the input mesh ("mm" = millimeters, "m" = meters)

    :return: the vertices and faces corresponding to the input mesh
    """

    vertices, faces = igl.read_triangle_mesh(path, 'float')

    if input_dimension == "m":
        vertices = vertices * 1000

    vertices, faces = clean(vertices, faces)

    print("number of faces after cleaning", len(faces))

    return vertices, faces


def remesh(vertices, faces, epsilon, edge_length):

    """
    We use fTetWild to mesh the volume of the surface boundary and re-extract the surface of the volume mesh as the resulting re-meshed surface.
    Please refer to https://github.com/wildmeshing/fTetWild for more information.

    :param vertices: list of vertex positions
    :param faces: list of triangle indices
    :param epsilon: the envelope of size epsilon. Using smaller envelope preserves features better but also takes longer time.
    :param edge_length: the ideal edge length. Using smaller ideal edge length gives a denser mesh but also takes longer time.

    :return: the set of vertices and faces of the re-meshed surface mesh
    """
    tetra = wm.Tetrahedralizer(epsilon=epsilon, edge_length_r=edge_length)
    tetra.set_mesh(vertices, faces)
    tetra.tetrahedralize()

    remesh_vertices, remesh_tets = tetra.get_tet_mesh()
    remesh_vertices, remesh_tets, _, _ = igl.remove_unreferenced(remesh_vertices, remesh_tets)

    # only keep the surface mesh
    remesh_faces = igl.boundary_facets(remesh_tets)

    # flip the normals
    flipped_remesh_faces = np.copy(remesh_faces)
    flipped_remesh_faces[:, [0, 1]] = flipped_remesh_faces[:, [1, 0]]

    rm_vertices, rm_faces = clean(remesh_vertices, flipped_remesh_faces)

    print('number of triangles after re-meshing', len(rm_faces))

    return rm_vertices, rm_faces


def get_curvature_measures(vertices,
                           faces,
                           neighbourhood_size,
                           curvature_type,
                           curve_info):

    """
    computes the curvature of a surface mesh and sets a corresponding curvature field for it

    :param vertices: list of vertex positions
    :param faces: list of triangle indices
    :param neighbourhood_size: controls the size of the neighbourhood used
    :param curvature_type: choose among "gaussian", "mean", "minimum" or "maximum"
    :param curve_info: If set to True, will visualize the curvature type on your model
    :return: assigned curvature value for for each face

    """

    # max_pd_v : #v by 3 maximal curvature direction for each vertex
    # min_pd_v : #v by 3 minimal curvature direction for each vertex
    # max_pv_v : #v by 1 maximal curvature value for each vertex
    # min_pv_v : #v by 1 minimal curvature value for each vertex
    max_pd_v, min_pd_v, max_pv_v, min_pv_v = igl.principal_curvature(vertices, faces, neighbourhood_size)

    # curvature onto face
    min_pv_f = igl.average_onto_faces(faces, min_pv_v)
    max_pv_f = igl.average_onto_faces(faces, max_pv_v)
    mean_pv_f = (min_pv_f + max_pv_f) / 2.0
    gaussian_pv_f = min_pv_f * max_pv_f

    # dictionary enabling selection of curvature measure
    selector = {"gaussian": gaussian_pv_f, "mean": mean_pv_f, "minimum": min_pv_f, "maximum": max_pv_f}

    # assign the selected curvature type
    curvature_value = selector[curvature_type]

    if curve_info:
        print(np.min(curvature_value))
        print(np.max(curvature_value))
        print(np.mean(curvature_value))

        frame = mp.subplot(vertices, faces, min_pv_f, s=[2, 2, 0])
        mp.subplot(vertices, faces, max_pv_f, s=[2, 2, 1], data=frame)
        mp.subplot(vertices, faces, mean_pv_f, s=[2, 2, 2], data=frame)
        mp.subplot(vertices, faces, gaussian_pv_f, s=[2, 2, 3], data=frame)

    return curvature_value


def get_initial_surface(vertices_p,
                        faces_p,
                        vertices_s,
                        faces_s,
                        gap_distance):

    """
    this function selects the initial subset of the primary surface

    :param vertices_p: list of vertex positions of the primary surface
    :param faces_p: list of triangle indices of the primary surface
    :param vertices_s: list of vertex positions of the secondary surface
    :param faces_s: list of triangle indices of the secondary surface
    :param gap_distance: distance threshold to select a subset of the primary surface as tissue attachment region
    :return: list of facet indices corresponding to the initial subset of the primary surface
    """
    # barycenter coordinate of each face
    triangle_centroids = igl.barycenter(vertices_p, faces_p)

    # sd_value: list of smallest signed distances
    # sd_face_idxs: list of facet indices corresponding to smallest distances
    # closest_points: closest points on the secondary surface to each point in triangle_centroids
    sd_value, sd_face_idxs, closest_points = igl.signed_distance(triangle_centroids,
                                                                 vertices_s, faces_s,
                                                                 return_normals=False)

    # list of facet indices below a distance threshold
    initial_face_idxs = np.where(sd_value < gap_distance)[0]

    # histogram
    y, x, _ = plt.hist(sd_value, bins=1000)
    ii = np.where(y == np.max(y))[0]
    # print('x =',x[ii])
    # plt.xlabel("distance from the primary to the secondary bone")
    # plt.ylabel("number of facets")
    # plt.show()

    # print('minimum joint space in HJ', np.round(np.min(sd_value),2))

    return initial_face_idxs, np.round(np.min(sd_value),2)


def get_initial_surface2(vertices_p,
                        faces_p,
                        vertices_s,
                        faces_s,
                        gap_distance):

    """
    This function selects the initial subset of the primary surface

    :param vertices_p: list of vertex positions of the primary surface
    :param faces_p: list of triangle indices of the primary surface
    :param vertices_s: list of vertex positions of the secondary surface
    :param faces_s: list of triangle indices of the secondary surface
    :param gap_distance: distance threshold to select a subset of the primary surface as tissue attachment region
    :return: list of facet indices corresponding to the initial subset of the primary surface
    """
    # barycenter coordinate of each face
    triangle_centroids = igl.barycenter(vertices_p, faces_p)

    # sd_value: list of smallest signed distances
    # sd_face_idxs: list of facet indices corresponding to smallest distances
    # closest_points: closest points on the secondary surface to each point in triangle_centroids

    vertex_p_idxs= np.unique(faces_p.flatten())
    sd_value, sd_face_idxs, closest_points = igl.signed_distance(triangle_centroids,
                                                                 vertices_s, faces_s,
                                                                 return_normals=False)

    # list of facet indices below a distance threshold
    initial_face_idxs = np.where(sd_value < gap_distance)[0]

    neigh_face_idxs = sd_face_idxs[initial_face_idxs]
    neigh_vertex_idxs= np.unique(faces_s[neigh_face_idxs].flatten())

    # histogram
    y, x, _ = plt.hist(sd_value, bins=1000)
    ii = np.where(y == np.max(y))[0]
    # print('x =',x[ii])
    # plt.xlabel("distance from the primary to the secondary bone")
    # plt.ylabel("number of facets")
    # plt.show()

    return initial_face_idxs, neigh_vertex_idxs


def get_initial_surface_bc(vertices_p,
                        faces_p,
                        vertices_s,
                        faces_s,
                        gap_distance):

    """
    This function selects the initial subset of the primary surface

    :param vertices_p: list of vertex positions of the primary surface
    :param faces_p: list of triangle indices of the primary surface
    :param vertices_s: list of vertex positions of the secondary surface
    :param faces_s: list of triangle indices of the secondary surface
    :param gap_distance: distance threshold to select a subset of the primary surface as tissue attachment region
    :return: list of facet indices corresponding to the initial subset of the primary surface
    """
    # barycenter coordinate of each face
    triangle_centroids = igl.barycenter(vertices_p, faces_p)

    # sd_value: list of smallest signed distances
    # sd_face_idxs: list of facet indices corresponding to smallest distances
    # closest_points: closest points on the secondary surface to each point in triangle_centroids

    sd_value, sd_face_idxs, closest_points = igl.signed_distance(triangle_centroids,
                                                                 vertices_s, faces_s,
                                                                 return_normals=False)

    # list of facet indices below a distance threshold
    initial_face_idxs = np.where(sd_value < gap_distance)[0]

    neigh_face_idxs = sd_face_idxs[initial_face_idxs]

    neigh_vertex_idxs= np.unique(faces_s[neigh_face_idxs].flatten())

    # histogram
    y, x, _ = plt.hist(sd_value, bins=1000)
    ii = np.where(y == np.max(y))[0]
    # print('x =',x[ii])
    # plt.xlabel("distance from the primary to the secondary bone")
    # plt.ylabel("number of facets")
    # plt.show()

    return initial_face_idxs, neigh_vertex_idxs


def get_boundary_faces(faces,
                       sub_face_idxs,
                       face_adjacency, cumulative_sum):

    """
    This function determines the facet indices belonging to the boundary of a sub-region.

    :param faces: list of faces where the sub-region is a part of
    :param sub_face_idxs: list of facet indices corresponding to the sub-region you want to find the boundary
    :param face_adjacency: The face adjacency matrix
    :param cumulative_sum: cumulative sum of "face-vertex visiting procedure" from libigl

    :return: Boundary face indices on both sides of the boundary and the inner boundary face indices
    """

    edge_vertex_idxs = igl.boundary_facets(faces[sub_face_idxs])
    boundary_vertex_idxs = np.unique(edge_vertex_idxs.flatten())

    boundary_face_idxs = []
    for j in boundary_vertex_idxs:
        for k in range(cumulative_sum[j], cumulative_sum[j + 1]):
            boundary_face_idxs += [face_adjacency[k]]
    inner_boundary_face_idxs = np.intersect1d(boundary_face_idxs, sub_face_idxs)

    return boundary_face_idxs, inner_boundary_face_idxs


def trim_boundary(faces,
                  sub_face_idxs,
                  face_adjacency,
                  cumulative_sum,
                  trimming_iteration):

    """
    This function trims the boundary of a sub-region.

    :param faces: list of faces where the sub-region is a part of
    :param sub_face_idxs: list of facet indices corresponding to the region you want to trim
    :param face_adjacency: the face adjacency matrix
    :param cumulative_sum: cumulative sum of "face-vertex visiting procedure" from libigl
    :param trimming_iteration: Number of trimming iterations to perform

    :return: list of facet indices corresponding to the trimmed sub-region
    """
    for i in range(trimming_iteration):
        b_face_idxs, ib_face_idxs = get_boundary_faces(faces, sub_face_idxs, face_adjacency, cumulative_sum)
        sub_face_idxs = np.setxor1d(sub_face_idxs, ib_face_idxs)

    return sub_face_idxs


def get_largest_component(faces,
                          sub_face_idxs):

    """
    This function only keeps the largest component of a sub-region.

    :param faces: list of faces where the sub-region is a part of
    :param sub_face_idxs: list of facet indices corresponding to the sub-region

    :return: list of facet indices corresponding to the largest component of the sub-region
    """

    components = igl.face_components(faces[sub_face_idxs])
    components_count = np.bincount(components)
    z = np.argmax(components_count)
    max_count = np.where(components == z)[0]
    single_face_idxs = sub_face_idxs[max_count]

    return single_face_idxs


def remove_ears(faces,
                sub_face_idxs):

    """
    This function removes any "ears" of the the sub-region.
    An "ear" refer to a single triangle with a vastly different normal than adjacent triangles
    See the illustration below for an example:

            ____/\____

    :param faces: list of faces where the sub-region is a part of
    :param sub_face_idxs: list of facet indices corresponding to the sub-region

    :return: list of facet indices corresponding to the sub-region with all the rears removed
    """

    ears = igl.ears(faces[sub_face_idxs])[0]
    cleaned_faces = np.delete(faces[sub_face_idxs], ears, axis=0)
    cleaned_face_idxs = []
    # TODO: Remove this for loop.
    for i in range(len(cleaned_faces)):
        ind = np.where(faces == cleaned_faces[i])[0]
        m = np.unique(ind, return_counts=True)[1]
        o = np.where(m == 3)[0][0]
        cleaned_face_idxs.append(ind[o])

    return np.array(cleaned_face_idxs)


def grow_cartilage(faces,
                   sub_face_idxs,
                   face_adjacency, cumulative_sum,
                   curvature_value,
                   min_curvature_threshold,
                   max_curvature_threshold):

    """
    This function grows the sub-region surface based on global curvature values.
    TODO: Change this to be based on local curvature

    :param faces: list of faces where the sub-region is a part of
    :param sub_face_idxs: list of facet indices corresponding to the sub-region
    :param face_adjacency: the face adjacency matrix
    :param cumulative_sum: cumulative sum of "face-vertex visiting procedure" from libigl
    :param curvature_value: assigned curvature value for for each face
    :param min_curvature_threshold: minimum curvature threshold for the grown region
    :param max_curvature_threshold: maximum curvature threshold for the grown region

    :return: list of facet indices corresponding to the grown sub-region
    """

    pending_face_idxs = sub_face_idxs
    faces_count = sub_face_idxs.shape[0]

    for n in range(200):

        # b = both side boundary, ib = inner boundary
        grow_b_face_idxs, grow_ib_face_idxs = get_boundary_faces(faces,
                                                                 pending_face_idxs,
                                                                 face_adjacency,
                                                                 cumulative_sum)

        # ob = the outer boundary
        grow_ob_face_idxs = np.setxor1d(grow_b_face_idxs, grow_ib_face_idxs)

        # neighbours with appropriate curvature range
        grow_measure = np.where(np.logical_and(curvature_value[grow_ob_face_idxs] > min_curvature_threshold,
                                               curvature_value[grow_ob_face_idxs] < max_curvature_threshold))
        grow_face_idxs = grow_ob_face_idxs[grow_measure]

        # add to the initial sub-region
        extended_face_idxs = np.concatenate((pending_face_idxs, grow_face_idxs))

        if extended_face_idxs.shape[0] == faces_count:
            break

        else:
            pending_face_idxs = extended_face_idxs
            faces_count = pending_face_idxs.shape[0]

    return extended_face_idxs


def assign_thickness(vertices_p,
                     faces_p,
                     vertices_s,
                     faces_s,
                     sub_face_idxs,
                     thickness_factor):

    """
    this function assigns a thickness to all the primary vertices.
    The thickness of all the vertices outside the sub-region is set to zero
    The thickness of all the vertices inside the sub-region is set to half of closest distance to the secondary surface

    :param vertices_p: list of vertex positions of the primary surface
    :param faces_p: list of triangle indices of the primary surface
    :param vertices_s: list of vertex positions of the secondary surface
    :param faces_s: list of triangle indices of the secondary surface
    :param sub_face_idxs: list of facet indices corresponding to the sub-region
    :param thickness_factor: a constant which will be multiplied by the distance between two surfaces.
    This allows you to control the thickness value

    :return: the thickness profile

    """
    sub_vertex_idxs = np.unique(faces_p[sub_face_idxs].flatten())
    sd_value = igl.signed_distance(vertices_p[sub_vertex_idxs], vertices_s, faces_s, return_normals=False)[0]
    sd_value = sd_value * thickness_factor

    # plt.hist(sd_value)
    # plt.show()

    minz = (np.min ( sd_value) + np.mean(sd_value) ) /2

    # thickness of all the vertices outside the sub-region
    thickness_profile = np.zeros(vertices_p.shape[0])

    # thickness of all the vertices inside the sub-region
    j = 0
    for i in sub_vertex_idxs:
        thickness_profile[i] = sd_value[j]
        j = j + 1

    return thickness_profile,  np.min ( sd_value)


def boundary_value(vertices,
                   faces,
                   external_boundary,
                   internal_boundary,
                   thickness_profile,
                   blending_order):

    """
    This function computes the value at the boundary.

    :param vertices:
    :param faces:
    :param external_boundary: external boundary vertex indices
    :param internal_boundary: internal boundary vertex indices
    :param thickness_profile: boundary values for all the vertices
    :param blending_order: power of harmonic operation (1: harmonic, 2: bi-harmonic, etc)

    :return: The harmonic weights determining how to interpolate between extruded and base surface
    """

    boundaries = np.concatenate((internal_boundary, external_boundary))

    boundary_thickness_value_outer = thickness_profile[external_boundary]
    boundary_thickness_value_inner = thickness_profile[internal_boundary]
    boundary_thickness_value = np.concatenate((boundary_thickness_value_inner, boundary_thickness_value_outer))

    weights = igl.harmonic_weights(vertices, faces, boundaries, boundary_thickness_value, blending_order)

    return weights


def extrude_cartilage(vertices_p,
                      faces_p,
                      sub_face_idxs,
                      harmonic_weights):

    """
    This function extrudes the subset surface based on harmonic weights.

    :param vertices_p: list of vertex positions of the primary surface
    :param faces_p: list of triangle indices of the primary surface
    :param sub_face_idxs: list of facet indices corresponding to the sub-region
    :param harmonic_weights: The harmonic weights computed by 'boundary_value'

    :return: extruded subset vertices
    """

    sub_vertex_idxs = np.unique(faces_p[sub_face_idxs].flatten())
    vertex_normals = igl.per_vertex_normals(vertices_p, faces_p)
    base_vertex_normals = vertex_normals[sub_vertex_idxs]

    thickness = []
    for i in range(len(sub_vertex_idxs)):
        thickness.append(base_vertex_normals [i] * harmonic_weights[i])

    extruded_vertices = np.copy(vertices_p)
    extruded_vertices[sub_vertex_idxs] = vertices_p[sub_vertex_idxs] + thickness

    return extruded_vertices


def extrude_uniform(vertices_p,
                    faces_p,
                    sub_face_idxs,
                    uniform_thickness):

    """
    This function extrudes the subset surface based on harmonic weights.

    :param vertices_p: list of vertex positions of the primary surface
    :param faces_p: list of triangle indices of the primary surface
    :param sub_face_idxs: list of facet indices corresponding to the sub-region
    :param uniform_thickness:

    :return: extruded subset vertices
    """

    sub_vertex_idxs = np.unique(faces_p[sub_face_idxs].flatten())
    vertex_normals = igl.per_vertex_normals(vertices_p, faces_p)
    base_vertex_normals = vertex_normals[sub_vertex_idxs]

    thickness = []
    for i in range(len(sub_vertex_idxs)):
        thickness.append(base_vertex_normals [i] * uniform_thickness)

    extruded_vertices = np.copy(vertices_p)
    extruded_vertices[sub_vertex_idxs] = vertices_p[sub_vertex_idxs] + thickness

    return extruded_vertices


def norm_visualization(vertices, faces):

    """
    This function visualizes the normal vector of each mesh face.
    :param vertices: list of vertices
    :param faces: list of faces

    :return: visualizes the norm of each facet
    """
    # starting point
    centroids = igl.barycenter(vertices, faces)
    face_normals = igl.per_face_normals(vertices, faces, np.array([1., 1., 1.]))
    avg_edge_length = igl.avg_edge_length(vertices, faces)

    # end point
    arrow_length = 2
    end_points = centroids + face_normals * avg_edge_length * arrow_length

    # visualization
    # frame = mp.plot(vertices, faces, c = pastel_yellow, shading = sh_true)
    # frame.add_lines(centroids, end_points, shading={"line_color": "aqua"})
    return centroids, end_points


def merge_surface_mesh(vertices_1,
                       faces_1,
                       vertices_2,
                       faces_2):

    """
    This function merges two surface meshes into one

    :param vertices_1: list of vertex positions of the first surface
    :param faces_1: list of faces of the first surface
    :param vertices_2: list of vertex positions of the second surface
    :param faces_2: list of faces of the second surface

    :return: The merged vertices and surfaces of the mesh
    """
    merged_vertices = np.concatenate((vertices_1, vertices_2))
    merged_faces = np.concatenate((faces_1, faces_2 + len(vertices_1)))

    return merged_vertices, merged_faces


def smooth_and_separate_boundaries(vertices,
                                   boundary_edges,
                                   vertices_b,
                                   faces_p,
                                   smoothing_factor,
                                   smoothing_iteration):

    """
    This function smooths the subset boundaries and ensures no penetration to the underlying surface.

    :param vertices: list of vertex positions
    :param boundary_edges: list of the boundary edge indices
    :param vertices_b:
    :param faces_p:
    :param smoothing_factor:
    :param smoothing_iteration: number of smoothing iterations to perform

    :return: list of separated, smooth and non-penetrating vertices
        
    """

    # determine and smooth first boundary
    boundary_1 = igl.edges_to_path(boundary_edges)[0]

    for i in range(smoothing_iteration):
        vertices = smooth_boundary(vertices, boundary_1, smoothing_factor)
        # vertices = snap_to_surface(vertices, vertices_b, faces_p)

    # determine if we have more boundaries and smooth them
    boundary_1_idxs = []
    for j in boundary_1:
        idx = np.where(boundary_edges == j)[0]
        boundary_1_idxs.append(idx)
    boundary_2_idxs = np.delete(boundary_edges, boundary_1_idxs, axis=0)

    if len(boundary_2_idxs) != 0:
        boundary_2 = igl.edges_to_path(boundary_2_idxs)[0]

        for i in range(smoothing_iteration):
            vertices = smooth_boundary(vertices, boundary_2, smoothing_factor)
            # vertices = snap_to_surface(vertices, vertices_b, faces_p)

    return vertices


def smooth_boundary(vertices, b_idxs, smoothing_factor):

    """
    This function smooths the boundary of the surface using Laplacian smoothing.

    :param vertices: list of vertex positions
    :param b_idxs:
    :param smoothing_factor:

    :return: list of smooth and non-penetrating vertices
    """
    # add the last vertex idxs to the beginning and the first index to the end
    b_idxs = np.insert(b_idxs, 0, b_idxs[-1])
    b_idxs = np.insert(b_idxs, len(b_idxs), b_idxs[1])
    
    # new vertices
    new_vertices = np.zeros((len(b_idxs) - 2, 3))
    
    # loop through all boundary vertices and apply smoothing
    for i in range(1, len(b_idxs) - 1):
        
        delta = 0.5 * ( vertices[ b_idxs[i - 1] ] + vertices[ b_idxs[i + 1] ] ) - vertices[ b_idxs[i] ]
        
        new_vertices[i - 1] = vertices[b_idxs[i]] + smoothing_factor * delta

    vertices[b_idxs[1: -1]] = new_vertices

    return vertices


def save_surface(vertices, faces, output_dim, path):

    """
    This function saves a surface mesh (obj file format) of the generated model

    :param vertices: list of vertex positions
    :param faces: list of the triangle faces
    :param output_dim: output dimension
    :param path: The path where the file should be saved at.

    """

    if output_dim == "m":
        vertices = vertices / 1000

    igl.write_triangle_mesh(path, vertices, faces)


def get_area(vertices, faces):

    """
    This function measures the surface area of a given surface mesh

    :param vertices: list of vertex positions
    :param faces: list of the triangle faces in which you want to measure the surface area

    :return: the surface area of the input triangles
    """

    surface_area = 0
    for i in range(len(faces)):
        u = vertices[faces[i, 1]] - vertices[faces[i, 0]]
        v = vertices[faces[i, 2]] - vertices[faces[i, 0]]
        n = np.cross(u, v)
        mag = np.linalg.norm(n, axis=0)
        mag = mag / 2

        surface_area += mag

    return surface_area


def make_cut_plane_view(vertices,
                        faces,
                        d=0,
                        s=0.5):

    """
    This function visualizes a plane cut view of a given mesh

    :param vertices: list of vertex positions
    :param faces: list of the triangle faces in which you want to see the cut-plane
    :param d: is the direction of the cut: x=0, y=1, z=2
    :param s: s it the size of the cut where 1 is equal to no cut and 0 removes the whole object
    """

    a = np.amin(vertices, axis=0)
    b = np.amax(vertices, axis=0)
    h = s * (b - a) + a
    c = igl.barycenter(vertices, faces)

    if d == 0:
        idx = np.where(c[:, 1] < h[1])
    elif d == 1:
        idx = np.where(c[:, 0] < h[0])
    else:
        idx = np.where(c[:, 2] < h[2])

    return idx


def get_wall(vertices_p, boundary_vertex_idxs1, boundary_vertex_idxs2 ):

    """
    This function ...

    :param vertices_p:
    :param boundary_vertex_idxs1:
    :param boundary_vertex_idxs2:

    :return: the face list of the discretized plane
    """
    internal_boundary = np.copy(boundary_vertex_idxs1)
    external_boundary = np.copy(boundary_vertex_idxs2)

    # closing the loop
    internal_boundary = np.append(internal_boundary, internal_boundary[0])
    external_boundary = np.append(external_boundary, external_boundary[0])

    # build the wall
    wall_faces = []

    for i in range(len(internal_boundary) - 1):
        z = [internal_boundary[i], external_boundary[i] + len(vertices_p),
             external_boundary[i + 1] + len(vertices_p)]
        x = [internal_boundary[i], external_boundary[i + 1] + len(vertices_p), internal_boundary[i + 1]]
        wall_faces.append(z)
        wall_faces.append(x)

    wall_faces = np.array(wall_faces)

    return wall_faces


def snap_to_surface ( vertices, vertices_r, faces_r ):

    """
    This function ...

    :param vertices:
    :param vertices_r:
    :param faces_r:
    :return:
    """

    vertices_p = np.copy (vertices)
    sd_value, _, closest_points = igl.signed_distance(vertices_p, vertices_r, faces_r, return_normals=False)
    vertices_p = closest_points

    return vertices_p


def refine_secondary_bone (vertices_p,
                           faces_p,
                           ex_base_b_vertex_idxs,
                           vertices_s,
                           faces_s,
                           vertices_b,
                           faces_b):

    """
    This function ...

    :param vertices_p:
    :param faces_p:
    :param ex_base_b_vertex_idxs:
    :param vertices_s:
    :param faces_s:
    :param vertices_b:
    :param faces_b:
    :return:
    """
    face_adjacency, cumulative_sum = igl.vertex_triangle_adjacency(faces_s, len(vertices_s))

    # find a subset:
    face_idxs = get_initial_surface(vertices_s, faces_s,  vertices_b, faces_b, 10)
    subset_s = faces_s[face_idxs]
    subset_vertex_idxs = np.unique(subset_s.flatten())

    #
    index_list = []
    distance = []
    for j in ex_base_b_vertex_idxs:
        for i in vertices_s[subset_vertex_idxs]:
            closest_vertex = np.linalg.norm(i - vertices_p[j])
            distance.append(closest_vertex)
        # print(distance)
        seed_idxs = np.where(distance == np.min(distance))[0]
        # print(seed_idxs)
        # seed_idx = np.array(seed_idxs[0])
        # print(seed_idx)
        distance = []
        index_list.append(seed_idxs[0])
    #
    index_list = np.array(index_list)
    # index_list = np.unique(index_list)
    print(len(ex_base_b_vertex_idxs))
    print(len(index_list))
    #
    vertex_idxs = subset_vertex_idxs[index_list]
    #
    s_face_idxs = []
    for j in vertex_idxs:
        for k in range(cumulative_sum[j], cumulative_sum[j + 1]):
            s_face_idxs += [face_adjacency[k]]

    frame = mp.plot(vertices_s, faces_s, c=bone, shading=sh_true)
    frame.add_points(vertices_p[ex_base_b_vertex_idxs], shading={"point_color": "green", "point_size": 3})
    frame.add_points(vertices_s[subset_vertex_idxs[index_list]], shading={"point_color": "red", "point_size": 3})
    # frame.add_mesh(vertices_s, faces_s, c= bone, shading = sh_true )
    frame.add_mesh(vertices_s, faces_s[s_face_idxs], c= pastel_green, shading = sh_true)

    mp.plot(vertices_s, faces_s[s_face_idxs], c= pastel_green, shading = sh_true)

    print(faces_s[s_face_idxs])

    ss_vertex_idxs = igl.boundary_loop(faces_s[s_face_idxs])
    print(ss_vertex_idxs)
    print('new', len(ss_vertex_idxs))



def remove_penetration (vertices, vertices_r, faces_r):

    """
    This function ...

    :param vertices:
    :param vertices_r:
    :param faces_r:
    :return:
    """
    vertices_p = np.copy(vertices)
    sd_value, _, closest_points = igl.signed_distance(vertices_p, vertices_r, faces_r, return_normals=False)
    penetrating_vertices = np.where(sd_value <= 0)[0]
    vertices_p[penetrating_vertices] = closest_points[penetrating_vertices]

    return vertices_p


def contact_surface(vertices_1,
                    faces_1,
                    vertices_2,
                    faces_2,
                    epsilon):

    """
    This function measured the contact surface in the cartilage-cartilage interface.

    :param vertices_1: vertices: list of vertex positions
    :param faces_1:
    :param vertices_2: list of vertex positions
    :param faces_2:
    :param epsilon:

    """

    # triangle centroids
    triangle_centroids = igl.barycenter(vertices_1, faces_1)

    # point to surface distance
    sd_value, _, _ = igl.signed_distance(triangle_centroids,
                                         vertices_2,
                                         faces_2,
                                         return_normals=False)

    print('min:', np.min(sd_value))

    # faces below a distance threshold
    contact_face_idxs = np.where(sd_value <= epsilon)[0]

    # viz
    frame = mp.plot(vertices_1, faces_1, c=bone, shading=sh_false)
    frame.add_mesh(vertices_1, faces_1[contact_face_idxs], c=organ, shading=sh_true)

    contact_area = get_area(vertices_1, faces_1[contact_face_idxs])

    print("contact surface area is: ", np.round(contact_area, 2))


def neighbouring_info(vertices, faces):

    """
    This function measured the contact surface in the cartilage-cartilage interface.

    :param vertices:
    :param faces:

    :return:

    """

    # adjacency info
    face_adjacency, cumulative_sum = igl.vertex_triangle_adjacency(faces, len(vertices))

    # part.1 boundary vertex indices
    boundary_vertex_idxs = igl.boundary_loop(faces)

    # part.2 neighboring faces to these vertices
    boundary_face_idxs = []
    container = []
    for j in boundary_vertex_idxs:
        for k in range(cumulative_sum[j], cumulative_sum[j + 1]):
            container += [face_adjacency[k]]
        boundary_face_idxs.append(container)
        container = []

    # part.3 find the face neighbors to these faces
    tt_info = igl.triangle_triangle_adjacency(faces)[0]

    container = []
    neigh_face_list = []
    for i in boundary_face_idxs:
        a = tt_info[i]
        a = np.unique(a.flatten())
        a = a.tolist()
        neigh_face_list.append(a[1:])
        a = 0

    return boundary_vertex_idxs, boundary_face_idxs, neigh_face_list


def get_dihedral_angle (vertices, faces, face_idxs, neigh_face_list ):

    """
    This function measured the contact surface in the cartilage-cartilage interface.

    :param vertices:
    :param faces:
    :param face_idxs:
    :param neigh_face_list:
    :return:
    """

    # face normals
    face_normals = igl.per_face_normals(vertices, faces[face_idxs], np.array([1., 1., 1.]))

    # measure dihedral angles
    container = []
    angles = []

    for i in neigh_face_list:
        # make all possible pairs
        pairs = []
        for j in range(len(i)):
            for k in range(len(i)):
                a = [i[j], i[k]]
                pairs.append(a)
        pairs = np.array(pairs)

        # find the dihedral angle of each pair
        for l in pairs:
            cos = np.dot(face_normals[l[0]], face_normals[l[1]])
            cos = np.clip(cos, -1, 1)
            container.append(np.arccos(cos))
        angles.append(container)
        container = []

    max_angles = []
    for i in angles:
        container = np.max(i)
        max_angles.append(container)
        container = []

    return max_angles


def fix_boundary(vertices, faces, face_idxs, boundary_vertex_idxs, folded_vertex_idxs ):

    """
    This function measured the contact surface in the cartilage-cartilage interface.

    :param vertices:
    :param faces:
    :param face_idxs:
    :param boundary_vertex_idxs:
    :param folded_vertex_idxs:
    :return:
    """

    # adjacency info
    face_adjacency, cumulative_sum = igl.vertex_triangle_adjacency(faces[face_idxs], len(vertices))

    container = []
    per_vertex_neighbour_face_idxs = []
    for i in boundary_vertex_idxs[folded_vertex_idxs]:
        for k in range(cumulative_sum[i], cumulative_sum[i + 1]):
            container += [face_adjacency[k]]
        per_vertex_neighbour_face_idxs.append(container)
        container = []

    all_neighbour_face_idxs = []
    for i in per_vertex_neighbour_face_idxs:
        for j in i:
            all_neighbour_face_idxs.append(j)

    all_array = np.array(all_neighbour_face_idxs)
    count = []
    for i in all_neighbour_face_idxs:
        count.append(all_neighbour_face_idxs.count(i))

    count = np.array(count)

    mutual = np.where(count == 2)[0]

    faulty_face_idxs = all_array[mutual]
    faulty_face_idxs = np.unique(faulty_face_idxs)

    # vz
    print("The pink triangles will be removed:")
    frame = mp.plot(vertices, faces[face_idxs], c=pastel_blue, shading=sh_false)
    frame.add_mesh(vertices, faces[face_idxs[faulty_face_idxs]], c=sweet_pink, shading=sh_true)

    face_idxs = np.delete(face_idxs, faulty_face_idxs, axis=0)

    return face_idxs


def fit_cylinder (vertices_p, faces_p, base_face_idxs):

    """

    :param vertices_p:
    :param faces_p:
    :param base_face_idxs:
    :return:
    """

    face_idxs = np.arange(len(faces_p))
    rest_face_idxs = np.delete(face_idxs, base_face_idxs, axis=0)

    # find the fovea region
    components = igl.face_components(faces_p[rest_face_idxs])
    components_count = np.bincount(components)
    z = np.argmin(components_count)
    max_count = np.where(components == z)[0]

    # face indices
    fovea_face_idxs = rest_face_idxs[max_count]

    # boundary vertex indices
    fovea_b_vertex_idxs = igl.boundary_loop(faces_p[fovea_face_idxs])

    # extrude positive

    fovea_top_vertices = extrude_uniform(vertices_p, faces_p, fovea_face_idxs, 2)
    fovea_bottom_vertices = extrude_uniform(vertices_p, faces_p, fovea_face_idxs, -2)


    # build wall
    base_faces = faces_p[fovea_face_idxs]

    # flip normals of the bottom surface
    flipped_faces_p = np.copy(faces_p)
    flipped_faces_p[:, [0, 1]] = flipped_faces_p[:, [1, 0]]

    # build wall
    wall_faces = get_wall(fovea_bottom_vertices,
                                 fovea_b_vertex_idxs, fovea_b_vertex_idxs)

    # merge left, top, and right faces
    si_vertices = np.concatenate((fovea_top_vertices, fovea_bottom_vertices))
    si_faces = np.concatenate((base_faces, wall_faces, flipped_faces_p[fovea_face_idxs] + len(fovea_top_vertices)))

    # final touch
    si_vertices, si_faces = clean(si_vertices, si_faces)

    return si_vertices, si_faces


def get_angle(o, p1, p2):

    """
    This function ...

    :param o:
    :param p1:
    :param p2:
    :return:
    """
    # vector
    v1 = p1 - o
    v2 = p2 - o

    # unit vector
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)

    # angle
    cos = np.clip(np.dot(v1_u, v2_u, out=None), -1, 1)

    rad = np.arccos(cos)
    theta = math.degrees(rad)

    return theta


def get_distance(p1, p2):

    """
    This function ...


    :param p1:
    :param p2:
    :return:
    """
    dist = np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)

    return dist


def build_edge(sar, l, wall_edges):
    """

    :param sar:
    :param l:
    :param wall_edges:
    :return:
    """

    for i in range(len(sar)):
        if sar[i][1] == 0:
            l[0] = sar[i][0]
        if sar[i][1] == 1:
            l[1] = sar[i][0]
        container = np.copy(l)
        wall_edges.append(container)
        container = []

    return wall_edges


def get_wall_sweep(t_vertices, t_faces, b_vertices, b_faces):

    """
    This function builds a wall surface mesh between two interfaces. Given the borders of the two interfaces, the sweep
    line algorithm passes an imaginary line through the border nodes and builds a discretized plane between them.

    :param t_vertices:
    :param t_faces:
    :param b_vertices:
    :param b_faces:
    :return:
    """

    # center point
    t_center = np.average(t_vertices, axis=0)
    t_center = np.array([t_center])

    b_center = np.average(b_vertices, axis=0)
    b_center = np.array([b_center])

    x_center = 0.5 * (b_center + t_center)

    sd, _, cd1 = igl.signed_distance(x_center, t_vertices, t_faces, return_normals=False)
    sd, _, cd2 = igl.signed_distance(x_center, b_vertices, b_faces, return_normals=False)
    cd1 = np.array([cd1])
    cd2 = np.array([cd2])
    #
    # frame = mp.plot(t_vertices, t_faces, c= pastel_blue, shading= sh_true)
    # frame.add_mesh(b_vertices, b_faces, c= pastel_yellow, shading=sh_true)
    # frame.add_points(t_center, shading={"point_size": 1, "point_color": "blue"})
    # frame.add_points(b_center, shading={"point_size": 1, "point_color": "blue"})
    # frame.add_points(cd1, shading={"point_size": 1, "point_color": "red"})
    # frame.add_points(cd2, shading={"point_size": 1, "point_color": "red"})
    # ##
    # boundary
    t_boundary_vertex_idxs = igl.boundary_loop(t_faces)
    b_boundary_vertex_idxs = igl.boundary_loop(b_faces)

    # print('top surface boundary has ', len(t_boundary_vertex_idxs), 'vertices')
    # print('bottom surface boundary has ', len(b_boundary_vertex_idxs), 'vertices')

    # print(b_boundary_vertex_idxs)
    b_boundary_vertex_idxs = b_boundary_vertex_idxs[::-1]
    # print(b_boundary_vertex_idxs)
    # frame = mp.plot(t_vertices, t_faces, c=pastel_yellow, shading={"wireframe": True})
    # frame.add_mesh(b_vertices, b_faces, c=bone, shading={"wireframe": True})
    # for i in t_boundary_vertex_idxs:
    #     frame.add_points(t_vertices[[i]],shading={"point_size": 5, "point_color": "red"})
    # for i in b_boundary_vertex_idxs:
    #     frame.add_points(b_vertices[[i]],shading={"point_size": 5, "point_color": "yellow"})

    ##
    # starting point on bottom
    b_start_idx = [b_boundary_vertex_idxs[0]]

    # starting point on top
    distance = []
    for i in t_boundary_vertex_idxs:
        dist = np.linalg.norm(t_vertices[i] - b_vertices[b_start_idx])
        distance.append(dist)

    idx = np.where(distance == np.min(distance))[0]
    t_start_idx = t_boundary_vertex_idxs[idx]

    # print('start index for the bottom surface', b_start_idx)
    # print('start index for the top surface', t_start_idx)

    # frame = mp.plot(t_vertices, t_faces, c=pastel_blue, shading=sh_true)
    # frame.add_mesh(b_vertices, b_faces, c=pastel_yellow, shading=sh_true)
    # frame.add_points(t_vertices[t_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "blue"})
    # frame.add_points(b_vertices[b_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "yellow"})
    # frame.add_points(b_vertices[b_start_idx], shading={"point_size": 2, "point_color": "red"})
    # frame.add_points(t_vertices[t_start_idx], shading={"point_size": 2, "point_color": "red"})
    ##
    # reorder the top surface based on the starting point
    closed_t_idxs = []

    for i in range(idx[0], len(t_boundary_vertex_idxs)):
        closed_t_idxs.append(t_boundary_vertex_idxs[i])

    for i in range(idx[0]):
        closed_t_idxs.append(t_boundary_vertex_idxs[i])
    ##
    # close the loop
    closed_t_idxs = np.append(closed_t_idxs, closed_t_idxs[0])
    closed_b_idxs = np.append(b_boundary_vertex_idxs, b_boundary_vertex_idxs[0])

    # print('top closed loop has ', len(closed_t_idxs), 'vertices')
    # print('bottom closed has ', len(closed_b_idxs), 'vertices')
    # print('')

    # print(closed_t_idxs)
    # print(closed_b_idxs)
    ##
    t_label = []
    for i in range(len(closed_t_idxs)):
        t_label.append(int(1))

    b_label = []
    for i in range(len(closed_b_idxs)):
        b_label.append(int(0))

    # print('top closed loop has ', len(t_label), 'labels (1)')
    # print('bottom closed has ', len(b_label), 'labels (0)')
    # print('')

    # print(t_label)
    # print(b_label)
    ##

    # measure angle
    angle_t = []
    bin_t = 0
    for i in range(len(closed_t_idxs) - 1):
        #     theta_t = get_angle (cd1[0] , t_vertices[closed_t_idxs[i]], t_vertices[closed_t_idxs[i+1]])
        theta_t = get_distance(t_vertices[closed_t_idxs[i]], t_vertices[closed_t_idxs[i + 1]])
        bin_t = bin_t + theta_t
        angle_t.append(bin_t)

    #
    angle_b = []
    bin_b = 0
    for i in range(len(closed_b_idxs) - 1):
        #     theta_b = get_angle (cd2[0] , b_vertices[closed_b_idxs[i]], b_vertices[closed_b_idxs[i+1]])
        theta_b = get_distance(b_vertices[closed_b_idxs[i]], b_vertices[closed_b_idxs[i + 1]])
        bin_b = bin_b + theta_b
        angle_b.append(bin_b)
    #
    angle_b.insert(0, 0)
    angle_t.insert(0, 0)
    #
    # print('angles in top points:')
    # print(np.round(angle_t, 3))
    # print('')
    #

    # angle_b = np.array(angle_b)
    # angle_b[1:] = angle_b[1:] - 0.582
    # print('angles in bottom points:')
    # print(np.round(angle_b, 3))

    # draw lines
    initial = [closed_b_idxs[0], closed_t_idxs[0]]
    # print(initial)

    # frame = mp.plot(t_vertices, t_faces, c=pastel_blue, shading={"wireframe": True})
    # frame.add_mesh(b_vertices, b_faces, c=pastel_green, shading={"wireframe": True})
    # frame.add_points(t_vertices[t_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "blue"})
    # frame.add_points(b_vertices[b_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "yellow"})
    # frame.add_points(b_vertices[b_start_idx], shading={"point_size": 2, "point_color": "red"})
    # frame.add_points(t_vertices[t_start_idx], shading={"point_size": 2, "point_color": "red"})
    # frame.add_lines(b_vertices[initial[0]], t_vertices[initial[1]], shading={"line_color": "red"})
    ##

    # remove unreferenced
    new_vertices_b = b_vertices[closed_b_idxs]
    new_vertices_t = t_vertices[closed_t_idxs]

    new_b_vertex_idxs = np.arange(len(closed_b_idxs))
    new_t_vertex_idxs = np.arange(len(closed_b_idxs), len(closed_b_idxs) + len(closed_t_idxs))

    all_vertices = np.concatenate((new_vertices_b, new_vertices_t))
    # combine vertex idxs (first bottom, then top)

    all_vertex_idxs = np.concatenate((new_b_vertex_idxs, new_t_vertex_idxs), dtype=int)
    all_labels = np.concatenate((b_label, t_label), dtype=int)
    all_angles = np.concatenate((angle_b, angle_t))
    all_vertices_x = np.concatenate((new_vertices_b[:, 0], new_vertices_t[:, 0]))
    all_vertices_y = np.concatenate((new_vertices_b[:, 1], new_vertices_t[:, 1]))
    all_vertices_z = np.concatenate((new_vertices_b[:, 2], new_vertices_t[:, 2]))

    base = np.zeros((len(all_labels), 6))
    base[:, 0] = all_vertex_idxs
    base[:, 1] = all_labels
    base[:, 2] = all_angles
    base[:, 3] = all_vertices_x
    base[:, 4] = all_vertices_y
    base[:, 5] = all_vertices_z

    sorted_base = base[np.argsort(base[:, 2])]
    # print(sorted_base[:10])
    ##

    # make a first edge to start with
    line = [sorted_base[0][0], sorted_base[1][0]]
    beg = np.copy(line)
    # print(line)

    # delete the initial line form the stack
    sorted_base = np.delete(sorted_base, [0, 1], 0)

    # start the sweeping
    wall_edges = []
    for i in range(len(sorted_base)):
        if sorted_base[i][1] == 0:
            line[0] = sorted_base[i][0]
        if sorted_base[i][1] == 1:
            line[1] = sorted_base[i][0]
        container = np.copy(line)
        wall_edges.append(container)
        container = []

    # print(wall_edges[0])
    # t = wall_edges[0]
    # wall_edges.insert(0,t)
    wall_edges.insert(0, beg)
    wall_edges = np.array(wall_edges, dtype=int)
    #
    # print(wall_edges)

    # # make a first edge to start with
    # x = [sorted_base[0][0], sorted_base[1][0]]
    # beg = np.copy(x)
    #
    # # delete the initial line form the stack
    # sorted_base = np.delete(sorted_base, [0, 1], 0)

    # ###
    # split = np.array_split(sorted_base, 60)
    # # split = np.array(split)
    #
    # # start the sweeping
    # wall_edges = []
    # for i in range(len(split)):
    #     wall_edges = build_edge(split[i], x, wall_edges)
    #     wall_edges = np.array(wall_edges, dtype=int)
    #     x = [wall_edges[-1][0], wall_edges[-1][1]]
    #
    #     wall_edges = wall_edges.tolist()
    #
    # ##
    # wall_edges.insert(0, beg)
    # wall_edges = np.array(wall_edges, dtype=int)

    ##

    frame = mp.plot(t_vertices, t_faces, c=pastel_blue, shading={"wireframe": False})
    frame.add_mesh(b_vertices, b_faces, c=pastel_green, shading={"wireframe": False})
    frame.add_points(t_vertices[t_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "blue"})
    frame.add_points(b_vertices[b_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "green"})
    frame.add_points(b_vertices[b_start_idx], shading={"point_size": 2, "point_color": "red"})
    frame.add_points(t_vertices[t_start_idx], shading={"point_size": 2, "point_color": "red"})
    frame.add_lines(all_vertices[wall_edges[:, 0]], all_vertices[wall_edges[:, 1]],
                    shading={"line_color": "black", "line_width": 5.0})
    # frame.add_lines(b_vertices[initial[0]], t_vertices[initial[1]], shading={"line_color": "red", "line_width": 5.0})
    ##

    # make triangles out of edges
    container = []
    face_list = []
    for i in range(len(wall_edges) - 1):
        a = wall_edges[i, :]
        a = a.tolist()
        b = wall_edges[i + 1, :]
        b = b.tolist()
        container += a, b
        container = np.array(container)
        container = container.flatten()
        _, idx = np.unique(container, return_index=True)
        container = container[np.sort(idx)]
        face_list.append(container)
        container = []

    face_list = np.array(face_list)
    face_list[:, [0, 2]] = face_list[:, [2, 0]]
    # print(face_list)

    ##
    # frame = mp.plot(t_vertices, t_faces, c=new_blue, shading={"wireframe": False})
    # frame.add_mesh(b_vertices, b_faces, c=new_green, shading={"wireframe": False})
    # frame.add_points(t_vertices[t_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "blue"})
    # frame.add_points(b_vertices[b_boundary_vertex_idxs], shading={"point_size": 1, "point_color": "green"})
    # frame.add_points(b_vertices[b_start_idx], shading={"point_size": 3, "point_color": "red"})
    # frame.add_points(t_vertices[t_start_idx], shading={"point_size": 3, "point_color": "red"})
    # frame.add_lines(all_vertices[wall_edges[:12, 0]], all_vertices[wall_edges[:12, 1]],
    #                 shading={"line_color": "black", "line_width": 0.03})
    #
    # for i in range (len(closed_t_idxs)-1):
    #
    #     frame.add_lines(t_vertices[closed_t_idxs[i]], t_vertices[closed_t_idxs[i+1]],
    #                 shading={"line_color": "black", "line_width": 0.5})
    #
    # for i in range(len(closed_b_idxs) - 1):
    #     frame.add_lines(b_vertices[closed_b_idxs[i]], b_vertices[closed_b_idxs[i + 1]],
    #                     shading={"line_color": "black", "line_width": 0.5})
    #
    # frame.add_mesh(all_vertices, face_list[:11], c=new_pink, shading={"wireframe": True})
    # frame.add_lines(b_vertices[initial[0]], t_vertices[initial[1]], shading={"line_color": "red", "line_width": 5.0})

    norm_visualization(all_vertices, face_list)

    return all_vertices, face_list


def gap_fill(vertices_s, b1_faces, surface_face_idxs, face_idxs, cumulative_sum):

    """
    This function...

    :param vertices_s:
    :param b1_faces:
    :param surface_face_idxs:
    :param face_idxs:
    :param cumulative_sum:
    :return:
    """

    gap_boundary_vertex_idxs = [2]
    l = igl.boundary_loop(b1_faces[surface_face_idxs])

    # frame = mp.plot(vertices_s, b1_faces, c=bone, shading=sh_false)
    # frame.add_mesh(vertices_s, b1_faces[surface_face_idxs], c=pastel_blue, shading=sh_true)
    # frame.add_points(vertices_s[l], shading={"point_size": 5, "point_color": "red"})

    while len(gap_boundary_vertex_idxs) != 0:

        # lines creating the edge [v1 v2]
        edgeline_vertex_idxs = igl.boundary_facets(b1_faces[surface_face_idxs])

        # boundary vertices
        all_boundary_vertex_idxs = edgeline_vertex_idxs.flatten()

        # select the outer loop
        l = igl.boundary_loop(b1_faces[surface_face_idxs])
        # print(l)
        # separate the outer boundary
        gap_boundary_vertex_idxs = np.setxor1d(all_boundary_vertex_idxs, l)

        if len(gap_boundary_vertex_idxs) == 0:
            break

        # both-side boundary face
        boundary_face_idxs = []

        for j in gap_boundary_vertex_idxs:
            for k in range(cumulative_sum[j], cumulative_sum[j + 1]):
                boundary_face_idxs += [face_idxs[k]]

        # inner layer of the boundary faces
        inner_boundary_face_idxs = np.intersect1d(boundary_face_idxs, surface_face_idxs)

        # choose the outer boundary layer
        ob_face_idxs = np.setxor1d(boundary_face_idxs, inner_boundary_face_idxs)

        # merge with the rest
        surface_face_idxs = np.concatenate((surface_face_idxs, ob_face_idxs))

    return surface_face_idxs


" Colors and Eye-candies"

# color definitions
pastel_light_blue = np.array([179, 205, 226]) / 255.
pastel_blue = np.array([111, 184, 210]) / 255.
bone = np.array([0.92, 0.90, 0.85])
pastel_orange = np.array([255, 126, 35]) / 255.
pastel_yellow = np.array([241, 214, 145]) / 255.
pastel_green = np.array([128, 174, 128]) / 255.
mandible = np.array([222, 198, 101]) / 255
tooth = np.array([255, 250, 220]) / 255
organ = np.array([221, 130, 101]) / 255.
green = np.array([128, 174, 128]) / 255.
blue = np.array([111, 184, 210]) / 255.
sweet_pink = np.array([0.9, 0.4, 0.45])  #230, 102, 115
rib = np.array([253, 232, 158]) / 255.
skin = np.array([242, 209, 177]) / 255.
chest = np.array([188, 95, 76]) / 255.
dark_bone = np.array ([217, 208, 184])/255
dark_red = np.array([179, 0, 0])/255
dark_blue = np.array([0, 90, 179])/255
dark_green = np.array([0, 179, 89])/255


new_pink = np.array([202, 102, 115]) / 255.
new_green = np.array([102, 202, 139]) / 255.
new_blue = np.array([102, 165, 202]) / 255.



# Meshplot settings
sh_true = {'wireframe': True, 'flat': True, 'side': 'FrontSide', 'reflectivity': 0.1, 'metalness': 0, "wire_width": 0.01, "colormap": "jet",'normalize':False}
sh_false = {'wireframe': False, 'flat': True, 'side': 'FrontSide', 'reflectivity': 0.1, 'metalness': 0, "colormap": "jet",'normalize':False}