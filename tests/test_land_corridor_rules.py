import unittest
from tools.land_corridor_rules import (
    classify_abs_meshblock, classify_nsw_tenure,
    ROLE_HARD_EXCLUSION, ROLE_POSITIVE, ROLE_SOFT_PENALTY, ROLE_VERY_HIGH_PENALTY,
)


class LandCorridorRulesTests(unittest.TestCase):
    def test_national_park_is_hard_constraint(self):
        r=classify_nsw_tenure('National Park','Nature Reserve')
        self.assertEqual(r.role,ROLE_HARD_EXCLUSION)

    def test_private_land_is_penalty_not_exclusion(self):
        r=classify_nsw_tenure('Private','Private Property')
        self.assertEqual(r.role,ROLE_SOFT_PENALTY)

    def test_crown_road_is_positive_corridor_evidence(self):
        r=classify_nsw_tenure('Crownland-Other','Crown Road')
        self.assertEqual(r.role,ROLE_POSITIVE)

    def test_residential_meshblock_is_high_penalty(self):
        r=classify_abs_meshblock('Residential')
        self.assertEqual(r.role,ROLE_VERY_HIGH_PENALTY)

    def test_industrial_is_lower_penalty_than_residential(self):
        residential=classify_abs_meshblock('Residential')
        industrial=classify_abs_meshblock('Industrial')
        self.assertGreater(residential.weight,industrial.weight)

if __name__=='__main__': unittest.main()
