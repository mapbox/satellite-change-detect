# tiledelta

from rasterio import features, Affine
from shapely.geometry import Polygon, MultiPolygon, mapping

from skimage.filters import roberts
from sklearn import decomposition
import numpy as np
from scipy.ndimage.filters import maximum_filter
import json

def compareGreys(greyimage_before, greyimage_after, high_percentile=10, mid_percentile=20):

    assert greyimage_before.shape == greyimage_after.shape

    # get some edges
    edge_roberts_before = roberts(greyimage_before)
    edge_roberts_after = roberts(greyimage_after)

    # pca on the edge arrays
    delta = np.dstack([edge_roberts_after.ravel(), edge_roberts_before.ravel()])[0]
    pca = decomposition.PCA(n_components=2, whiten=False)
    pca.fit(delta)
    XY = pca.transform(delta)[:,1].reshape(greyimage_before.shape)
    XY = maximum_filter(XY, 3)

    # set areas below given percentile thresholds
    midperc = np.percentile(XY, mid_percentile)
    highperc = np.percentile(XY, high_percentile)

    out = np.zeros((XY.shape), dtype=np.uint8)

    out[np.where(XY <= midperc)] = 1
    out[np.where(XY <= highperc)] = 2

    return out

def getXYZ(fileinfo):
    X = int(fileinfo[1])
    Y = int(fileinfo[2])
    Z = int(fileinfo[3].split('.')[0])
    return X, Y, Z

def makeAffine(imageshape, bounds):

    cellsizeX = (bounds[2] - bounds[0]) / float(imageshape[1])
    cellsizeY = (bounds[3] - bounds[1]) / float(imageshape[0])

    return Affine(
        cellsizeX, 0.0, bounds[0],
        0, -cellsizeY, bounds[3]
    )

def makeVectors(inArr, affine_trans):
    for feature, shapes in features.shapes(np.asarray(inArr,order='C'),transform=affine_trans):
        if shapes != 0:
            featurelist = [Polygon(f) for f in feature['coordinates']]
            print json.dumps({
                        'type': 'Feature',
                        'geometry': mapping(MultiPolygon(featurelist)),
                        'properties': {
                            'pred_delta': shapes
                        }
                })