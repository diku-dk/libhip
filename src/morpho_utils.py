import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from vtk.numpy_interface import dataset_adapter as dsa

from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression


def read_centerline(path):
    reader = vtk.vtkPolyDataReader()
    reader.SetFileName(path)
    reader.ReadAllScalarsOn()
    reader.ReadAllVectorsOn()
    reader.Update()
    polydata = reader.GetOutput()
    numpy_array_of_points = dsa.WrapDataObject(polydata).Points
    return np.array(numpy_array_of_points)

def order_centerline (centerline):
    # extract the first and last array
    first = centerline[0]
    last = centerline[-1]

    # reorder if necessary
    if abs(first[2]) > abs(last[2]):
        centerline = centerline[::-1]

    return centerline


def polynomial_regression3d(x, y, z, degree):
    # sort data to avoid plotting problems
    x, y, z = zip(*sorted(zip(x, y, z)))

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    data_yz = np.array([y, z])
    data_yz = data_yz.transpose()

    polynomial_features = PolynomialFeatures(degree=degree)
    x_poly = polynomial_features.fit_transform(x[:, np.newaxis])

    model = LinearRegression()
    model.fit(x_poly, data_yz)
    y_poly_pred = model.predict(x_poly)

    # rmse = np.sqrt(mean_squared_error(data_yz, y_poly_pred))
    # r2 = r2_score(data_yz, y_poly_pred)
    # print("RMSE:", rmse)
    # print("R-squared", r2)

    # plot
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter(x, data_yz[:, 0], data_yz[:, 1])
    ax.plot(x, y_poly_pred[:, 0], y_poly_pred[:, 1], color='r')
    #     ax.scatter(centerline[182,0], centerline[182,1], centerline[182,2], color='g')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()
    fig.set_dpi(150)

    p1 = [x[0], y_poly_pred[0, 0], y_poly_pred[0, 1]]
    p2 = [x[-1], y_poly_pred[-1, 0], y_poly_pred[-1, 1]]

    a = []
    for i in range(len(x)):
        t = [x[i], y_poly_pred[i, 0], y_poly_pred[i, 1]]
        a.append(t)

    a = np.array(a)
    return np.array(p1), np.array(p2), a


def nsa(top_vec, bottom_vec):
    nsa = 180 * angle(top_vec, bottom_vec) / np.pi

    if nsa < 90:
        nsa = 180 - nsa

    return nsa

def angle(vector_1, vector_2):

    unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
    unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    angle = np.arccos(dot_product)

    return angle
