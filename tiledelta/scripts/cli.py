#!/usr/bin/env python

from sklearn import decomposition
import rasterio as rio
import numpy as np
import click, json, os
import urllib, tiledelta

@click.group()
def cli():
    pass

@click.command(short_help="HELP")
@click.argument('bounds', default='-', required=False)
@click.option('--stride', default=1)
def loaddata(bounds, stride):
    """Does something"""
    try:
        inBounds = click.open_file(bounds).readlines()
    except IOError:
        inBounds = [bounds]
    bounds = json.loads(inBounds[0])
    click.echo(bounds['bbox'])
    # with rio.drivers():
    #     with rio.open('src_path', 'r') as src:

cli.add_command(loaddata)

@click.command(short_help="HELP")
@click.argument('url')
@click.argument('z')
@click.argument('x')
@click.argument('y')
@click.argument('save_dir')
def loadimage(url, z, x, y, save_dir):
    """Does something"""
    getUrl = url % (z, x, y,)
    fileext = getUrl.split('.')[-3][0:3]
    saveFile = save_dir + 'tile-%s-%s-%s.%s' % (x, y, z, fileext)
    urllib.urlretrieve (getUrl, saveFile)

cli.add_command(loadimage)


@click.command()
@click.argument('filedir', type=click.Path(exists=True))
def anaimage(filedir):
    import matplotlib.pyplot as plot
    from skimage.filters import roberts
    files = os.listdir(filedir)
    ctr = 1
    fig = plot.figure(figsize=(50,50))
    for f in files:
        fileinfo = f.split('-')
        if len(fileinfo[-1].split('.')) != 0 and fileinfo[-1].split('.')[-1] == 'png':
            with rio.drivers():
                with rio.open(os.path.join(filedir, f), 'r') as src:
                    edge_roberts = roberts(src.read(1))
                    ax = fig.add_subplot(10,22,ctr)
                    # print ax
                    ax.imshow(edge_roberts)
                    ctr +=1
                    ax2 = fig.add_subplot(10,22,ctr)
                    ctr+=1
                    ax2.imshow(src.read(1))
    fig.savefig('/Users/dnomadb/Documents/test.png')
                    # yield [int(fileinfo[1]),int(fileinfo[2]),np.mean(edge_roberts)]


cli.add_command(anaimage)

@click.command()
@click.argument('filedir', type=click.Path(exists=True))
@click.argument('comparedir', type=click.Path(exists=True))
def compimage(filedir, comparedir):
    import matplotlib.pyplot as plot
    from skimage.filters import roberts
    from scipy.ndimage.filters import minimum_filter
    files = os.listdir(filedir)
    cfiles = os.listdir(comparedir)
    # ctr = 1
    # fig = plot.figure(figsize=(50,50))
    for f in files:
        fileinfo = f.split('-')
        if len(fileinfo[-1].split('.')) != 0 and fileinfo[-1].split('.')[-1] == 'png':
            with rio.drivers():
                with rio.open(os.path.join(filedir, f), 'r') as src:
                    greyimage_before = (src.read(1).astype(np.uint16) + src.read(2).astype(np.uint16) + src.read(3).astype(np.uint16))
                    edge_roberts_before = roberts(greyimage_before)
                with rio.open(os.path.join(comparedir, f), 'r') as src:
                    greyimage_after = (src.read(1).astype(np.uint16) + src.read(2).astype(np.uint16) + src.read(3).astype(np.uint16))
                    edge_roberts_after = roberts(greyimage_after)
                RB = np.dstack([edge_roberts_after.ravel(), edge_roberts_before.ravel()])[0]
                pca = decomposition.PCA(n_components=2, whiten=False)
                pca.fit(RB)
                X = pca.transform(RB)
                fig = plot.figure(figsize=(20,10))
                before = fig.add_subplot(131)
                before.imshow(greyimage_after,cmap='Greys_r')
                after = fig.add_subplot(132)
                after.imshow(greyimage_before, cmap='Greys_r')
                pcplo = X[:,1].reshape(512,512)
                pcperc = np.percentile(pcplo,5)
                pcplo[np.where(pcplo > pcperc)] = pcperc
                pcplo = minimum_filter(pcplo, 3)
                pc2 = fig.add_subplot(133)
                pc2.imshow(pcplo, cmap='YlGnBu')
                fig.savefig(os.path.join('/Users/dnomadb/Documents/pcomp', f))

cli.add_command(compimage)


if __name__ == '__main__':
    cli()

