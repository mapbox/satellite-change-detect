# satellite-change-detect
=========================

## tiledelta [very dev]

Given input directories of before and after image tiles, calculates relative change by:

 - Creating a grayscale image of the input bands
 - Calculates edges (roberts cross method)
 - Performs a principal component analysis on these two edge arrays
 - The second principal component of the above is then cut into classes, and either plotted w/ side-by-side before and after images, or
 - Vectorized into a geojson feature stream (useful for piping into [`tippecanoe`](https://github.com/mapbox/tippecanoe) for creation of Mapbox Vector Tiles)

### Install

`git clone` this repo and `cd` into it

then

`pip install -e .`

### Usage

```
tiledelta comptiles [OPTIONS] FILEDIR COMPAREDIR

Options:
  -s, --sampling INTEGER
  -f, --filetype TEXT
  -p, --plotdir PATH
  --help                  Show this message and exit.
```
eg

```
tiledelta comptiles /Users/dnomadb/test_kath/ /Users/dnomadb/test_before/ -s 1 | tippecanoe -o test.mbtiles -z 15 -Z 11 -f
```
makes valid vector tiles expressing the degree of change for that location.