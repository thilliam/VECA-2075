import importlib.util
from pathlib import Path
import unittest

import numpy as np
from rasterio.transform import from_origin

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('hstpath',ROOT/'tools'/'build_hst_terrain_path.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

class TestHstTerrainPath(unittest.TestCase):
    def test_astar_crosses_flat_surface(self):
        elev=np.zeros((20,20),dtype='float32')
        slope=np.zeros_like(elev)
        tx=from_origin(0,40000,2000,2000)
        path,cost=h.astar(elev,slope,tx,(1,1),(18,18),2000,3.0,0.65)
        self.assertEqual(path[0],(1,1));self.assertEqual(path[-1],(18,18))
        self.assertGreater(len(path),1);self.assertGreater(cost,0)

    def test_grade_envelope(self):
        chain=np.arange(0,11000,1000,dtype='float64')
        ground=np.array([0,0,0,150,300,450,300,150,0,0,0],dtype='float64')
        design=h.build_design_profile(ground,chain,0.035,4.0,1000)
        grades=np.abs(np.diff(design)/np.diff(chain))
        self.assertLessEqual(float(grades.max()),0.0350001)
        self.assertAlmostEqual(design[0],ground[0]);self.assertAlmostEqual(design[-1],ground[-1])

    def test_construction_thresholds(self):
        self.assertEqual(h.construction_mode(-30),'tunnel')
        self.assertEqual(h.construction_mode(-10),'cutting')
        self.assertEqual(h.construction_mode(0),'at_grade')
        self.assertEqual(h.construction_mode(6),'embankment')
        self.assertEqual(h.construction_mode(20),'bridge_or_elevated')

if __name__=='__main__': unittest.main()
