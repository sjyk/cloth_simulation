import numpy as np
import sys, pickle
from math import sqrt
from scipy.interpolate import interp1d

def load_robot_points(fname="calibration_data/gauze_pts.p"):
    """
    Loads a set of robot frame points from a pickle file.
    """
    lst = []
    f3 = open(fname,"rb")
    while True:
        try:
            pos2 = pickle.load(f3)
            lst.append(pos2)
        except EOFError:
            f3.close()
            return np.matrix(lst)

def get_basis(corners):
    """
    Finds a basis from corners where v1 and v2 are vectors denoting two edges of the robot frame gauze. V3 is a vector perpendicular to these two vectors, thus forming a basis in R^3.
    """
    v1 = np.array(corners[1]) - np.array(corners[0])
    v2 = np.array(corners[2]) - np.array(corners[0])
    v3 = np.cross(v1, v2)
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    v3 = v3 / np.linalg.norm(v3)
    return np.matrix(np.vstack((v1, v2, v3)).T)


def get_scale(corners, px_distance=500):
    """
    Finds the scale of a pixel in robot frame.
    """
    return  float(px_distance) / np.linalg.norm(np.array(corners[0]) - np.array(corners[1]))

def transform_and_project_point(transform, scale, pt, corners, offset=(50,50)):
    """
    Takes a point in robot frame and projects it onto the cloth object's plane.
    """
    return np.ravel(np.matrix(transform) * np.matrix((np.array(pt)  - np.array(corners[0]))).T * scale)[:2] + np.array(offset)

def get_shape_fn(corners, pts, interpolate=False):
    """
    Finds a function that represents the shape outlined by pts in robot frame, in the cloth simulation object's coordinate frame.
    """
    scale = get_scale(corners)
    basis = get_basis(corners)
    pxpts = []
    for pt in pts:
        pxpts.append(transform_and_project_point(basis, scale, pt, corners).tolist())
    if interpolate:
        pxpts = interpolation(np.array(pxpts), 10).tolist()
    return lambda x, y: np.min(np.linalg.norm(np.matrix(np.tile(np.array((x, y)), (len(pxpts), 1))) - pxpts, axis=1)) < 20

def get_trajectory(corners, pts, interpolate=True):
    """
    Finds a list that represents the trajectory outlined by pts in robot frame, in the cloth simulation object's coordinate frame.
    """
    scale = get_scale(corners)
    basis = get_basis(corners)
    pxpts = []
    for pt in pts:
        pxpts.append(transform_and_project_point(basis, scale, pt, corners).tolist())
    if interpolate:
        pxpts = interpolation(np.array(pxpts), 10).tolist()
    return pxpts

def get_robot_trajectory(pts, factor=10):
    """
    Returns the interpolated trajectory of pts in robot space.
    """
    return interpolation(np.array(pts), factor, True)

def interpolation(arr, factor, z_exists=False):
    """
    Given a matrix of x,y coordinates, output a linearly interpolated matrix of coordinates with factor * arr.shape[0] points.
    """
    x = arr[:, 0]
    y = arr[:, 1]
    if z_exists:
        z = arr[:,2]
    t = np.linspace(0,x.shape[0],num=x.shape[0])
    to_expand = [x, y]
    if z_exists:
        to_expand = [x, y, z]
    for i in range(len(to_expand)):
        spl = interp1d(t, np.ravel(to_expand[i]))
        to_expand[i] = spl(np.linspace(0,len(t), len(t)*factor))
    new_matrix = np.matrix(np.r_[0:len(t):1.0/factor])
    for i in to_expand:
        new_matrix = np.concatenate((new_matrix, np.matrix(i)), axis = 0)
    return new_matrix.T[:,1:]

if __name__ == "__main__":
    # corners = [(1, 1, 0), (2, 1, 0), (1, 2, 0), (2, 2, 0)]
    # fn = get_shape_fn(corners, [[2, 0, 0], [2,1,0], [2,2,0]])

    corners = load_robot_points()
    pts = load_robot_points("gauze_pts2.p")

    shape_fn = get_shape_fn(corners, pts, True)
