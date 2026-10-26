"""Exercise real dependency APIs used by the notebooks, without subject data."""

import importlib
import io
from pathlib import Path
import subprocess
import sys

import igl
import meshio
import meshplot as mp
import numpy as np
import pandas as pd
import pytest

import src


@pytest.fixture
def tetrahedron():
    vertices = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
    faces = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
    return vertices, faces


def test_notebook_dependencies_import():
    for module in ("miniball", "vtk", "sklearn", "yaml", "wildmeshing", "ipykernel", "notebook"):
        importlib.import_module(module)


def test_surface_cleanup_and_reading(tetrahedron, tmp_path):
    vertices, faces = tetrahedron
    # A duplicate position and an unused vertex exercise both remapping steps.
    vertices = np.vstack((vertices, vertices[0], [9., 9., 9.]))
    faces = faces.copy()
    faces[0, 0] = 4
    clean_v, clean_f = src.clean(vertices, faces)
    assert clean_v.shape == (4, 3)
    assert clean_f.shape == (4, 3)
    path = tmp_path / "tetra.obj"
    igl.write_triangle_mesh(path, vertices, faces)
    read_v, read_f = src.read_and_clean(path, "mm")
    np.testing.assert_allclose(read_v, clean_v)
    np.testing.assert_array_equal(read_f, clean_f)
    meter_v, _ = src.read(path, "m")
    np.testing.assert_allclose(meter_v, vertices * 1000)


def test_largest_component(tetrahedron):
    _, faces = tetrahedron
    faces = np.vstack((faces, [4, 5, 6]))
    np.testing.assert_array_equal(src.get_largest_component(faces, np.arange(5)), np.arange(4))


def test_distance_thickness_and_projection(tetrahedron):
    vertices, faces = tetrahedron
    plane_v = np.array([[0., 0., 2.], [10., 0., 2.], [0., 10., 2.]])
    plane_f = np.array([[0, 1, 2]])
    profile, minimum = src.assign_thickness(plane_v, plane_f, vertices, faces, np.array([0]), 0.5)
    assert np.all(np.isfinite(profile))
    assert minimum > 0
    projected = src.snap_to_surface(np.array([[0.2, 0.2, -1.]]), vertices, faces)
    np.testing.assert_allclose(projected, [[0.2, 0.2, 0.]])
    winding = igl.fast_winding_number(vertices, faces, np.array([[0.1, 0.1, 0.1], [2., 2., 2.]]))
    # The fast winding number is approximate; exercise the classifier threshold.
    np.testing.assert_array_equal(winding > 0.1, [True, False])


def test_harmonic_interpolation_and_extrusion():
    vertices = np.array([[0., 0., 0.], [1., 0., 0.], [1., 1., 0.], [0., 1., 0.], [0.5, 0.5, 0.]])
    faces = np.array([[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]])
    weights = src.boundary_value(vertices, faces, np.array([0, 3]), np.array([1, 2]), np.array([0., 1., 1., 0., 0.]), 1)
    np.testing.assert_allclose(weights, [0., 1., 1., 0., 0.5])
    extruded = src.extrude_cartilage(vertices, faces, np.arange(4), weights)
    np.testing.assert_allclose(extruded[:, 2], weights)
    distances = igl.exact_geodesic(vertices, faces, VS=np.array([0]), VT=np.arange(5))
    np.testing.assert_allclose(distances, np.linalg.norm(vertices - vertices[0], axis=1))


def test_curvature(tetrahedron):
    vertices, faces = tetrahedron
    values = src.get_curvature_measures(vertices, faces, 2, "mean", False)
    assert values.shape == (4,)
    assert np.all(np.isfinite(values))


def test_volume_mesh_roundtrip(tetrahedron, tmp_path):
    vertices, _ = tetrahedron
    elements = np.array([[0, 1, 2, 3]])
    labels = [np.array([1])]
    path = tmp_path / "volume.msh"
    meshio.write_points_cells(path, vertices, [("tetra", elements)], cell_data={"gmsh:physical": labels, "gmsh:geometrical": labels}, file_format="gmsh22", binary=False)
    actual_v, actual_e = src.read_volume_mesh(path, "mm", "mm")
    np.testing.assert_allclose(actual_v, vertices)
    np.testing.assert_array_equal(actual_e, elements)


@pytest.mark.native
def test_native_remeshing():
    # Run native code in isolation so a mesher stall cannot hang pytest.
    # Use an irregular tetrahedron rather than a symmetric fixture.
    code = """
import igl
import numpy as np
import src
vertices = np.array([[0., 0., 0.], [1.1, .1, .03], [.07, 1.2, .04], [.1, .05, .9]])
faces = np.array([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]])
v, f = src.remesh(vertices, faces, 0.01, 0.5)
assert v.shape[1] == 3
assert len(f) >= 4
assert len(igl.boundary_facets(f)[0]) == 0
"""
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_meshplot_widget_and_scalar_colors(tetrahedron):
    vertices, faces = tetrahedron
    viewer = mp.Viewer({})
    viewer.add_mesh(vertices, faces, c=np.arange(4, dtype=float), shading=src.sh_true)
    viewer.add_points(vertices, c=np.arange(4, dtype=float))
    html = viewer.to_html()
    assert "jupyter-threejs" in html


def test_mixed_anatomical_measurements():
    # Pandas 3 infers string columns; measurements must explicitly stay mixed.
    df = pd.read_csv(io.StringIO("Value\nm1\nempty\n"), dtype={"Value": object})
    df.loc[1, "Value"] = np.float64(1.25)
    assert df.loc[1, "Value"] == 1.25


@pytest.mark.parametrize("config", sorted(Path("config").glob("m*_config.yml")))
def test_subject_configs(config):
    assert src.Config(config).vol_var.epsilon
