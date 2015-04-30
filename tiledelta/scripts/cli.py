#!/usr/bin/env python

import rasterio as rio
import numpy as np
import click, json, os
import tiledelta, mercantile
from scipy.ndimage.filters import minimum_filter, maximum_filter

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


@click.command()
@click.argument('filedir', type=click.Path(exists=True))
@click.argument('comparedir', type=click.Path(exists=True))
@click.option('--sampling', '-s', type=(int), default=0)
def compimage(filedir, comparedir, sampling):

    plotdir = '/Users/dnomadb/Documents/pcomp'

    files = os.listdir(filedir)
    cfiles = os.listdir(comparedir)

    if plotdir:
        import matplotlib.pyplot as plot

    for f in files:
        fileinfo = f.split('-')
        if len(fileinfo[-1].split('.')) != 0 and fileinfo[-1].split('.')[-1] == 'png':
            x, y, z = tiledelta.getXYZ(fileinfo)
            bbox = mercantile.bounds(x, y, z)
            with rio.drivers():
                with rio.open(os.path.join(filedir, f), 'r') as src:
                    greyimage_before = (src.read(1).astype(np.uint16) + src.read(2).astype(np.uint16) + src.read(3).astype(np.uint16))
                with rio.open(os.path.join(comparedir, f), 'r') as src:
                    greyimage_after = (src.read(1).astype(np.uint16) + src.read(2).astype(np.uint16) + src.read(3).astype(np.uint16))
                
                pcplo = tiledelta.compareGreys(greyimage_after, greyimage_before, 10, 20)
                pcplo = pcplo[::sampling,::sampling]

                tiledelta.makeVectors(pcplo, tiledelta.makeAffine(pcplo.shape, bbox))

                
                if plotdir:
                    fig = plot.figure(figsize=(20,10))
                    before = fig.add_subplot(131)
                    before.imshow(greyimage_after,cmap='Greys_r')
                    after = fig.add_subplot(132)
                    after.imshow(greyimage_before, cmap='Greys_r')
                    pc2 = fig.add_subplot(133)
                    pc2.imshow(pcplo, cmap='YlGnBu')
                    fig.savefig(os.path.join(plotdir, f))

cli.add_command(compimage)


if __name__ == '__main__':
    cli()

