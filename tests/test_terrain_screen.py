import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_terrain_screen as terrain


class TerrainScreenTests(unittest.TestCase):
    def test_plane_slope_degrees(self):
        resolution = 100.0
        theta = 10.0
        rise_per_m = math.tan(math.radians(theta))
        x = np.arange(40, dtype=float) * resolution
        z = np.tile(x * rise_per_m, (30, 1))
        dem = np.ma.array(z, mask=np.zeros_like(z, dtype=bool))
        slope = terrain.slope_degrees(dem, int(resolution))
        self.assertAlmostEqual(float(np.ma.median(slope)), theta, delta=0.05)

    def test_band_edges(self):
        self.assertEqual(terrain.band_name(0), "very_low_gradient")
        self.assertEqual(terrain.band_name(2.999), "very_low_gradient")
        self.assertEqual(terrain.band_name(3), "low_gradient")
        self.assertEqual(terrain.band_name(8), "moderate_gradient")
        self.assertEqual(terrain.band_name(15), "steep")
        self.assertEqual(terrain.band_name(25), "very_steep")

    def test_aggregation_preserves_continuous_metrics(self):
        dem = np.ma.array(np.arange(64, dtype=float).reshape(8, 8))
        slope = np.ma.array(np.full((8, 8), 6.0, dtype=float))
        factor, metrics = terrain.aggregate_map_grid(dem, slope, 400, 100)
        elev_mean, slope_median, slope_p90, steep_share, valid_share = metrics
        self.assertEqual(factor, 4)
        self.assertEqual(elev_mean.shape, (2, 2))
        self.assertTrue(np.allclose(slope_median, 6.0))
        self.assertTrue(np.allclose(slope_p90, 6.0))
        self.assertTrue(np.allclose(steep_share, 0.0))
        self.assertTrue(np.allclose(valid_share, 1.0))


if __name__ == "__main__":
    unittest.main()
