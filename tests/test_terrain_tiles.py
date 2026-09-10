import unittest

import numpy as np

from tools import build_terrain_tiles as tiles


class TerrainTileTests(unittest.TestCase):
    def test_band_colours_keep_nodata_transparent(self):
        a=np.array([[2.0,10.0],[30.0,np.nan]],dtype=float)
        rgba=tiles.colour_bands(a)
        self.assertEqual(rgba.shape,(2,2,4))
        self.assertEqual(int(rgba[1,1,3]),0)
        self.assertGreater(int(rgba[0,0,3]),0)

    def test_colour_ramp_is_rgba(self):
        a=np.array([[0.0,5.0,20.0]],dtype=float)
        rgba=tiles.colour_ramp(a,tiles.SLOPE_STOPS)
        self.assertEqual(rgba.shape,(1,3,4))
        self.assertTrue(np.all(rgba[...,3]>0))

    def test_tile_bounds_have_positive_extent(self):
        x,y=tiles.lonlat_to_tile(151.2093,-33.8688,9)
        left,bottom,right,top=tiles.tile_bounds_3857(x,y,9)
        self.assertLess(left,right)
        self.assertLess(bottom,top)


if __name__=='__main__':
    unittest.main()
