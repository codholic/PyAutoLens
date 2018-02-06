import pytest
import numpy as np
import source_plane as sp
import math


# TODO : Work out some more test cases, particularly for the border_pixels / move factors / relocate routines
# TODO : Need to add functionality for sub-coordinates.

class TestSourcePlane(object):
    class TestInit(object):
        def test__sets_correct_values(self):
            coordinates = [(1.0, 1.0), (0.0, 0.5)]

            source_plane = sp.SourcePlane(coordinates)

            assert source_plane.coordinates == [(1.0, 1.0), (0.0, 0.5)]

        def test__four_coordinates__correct_source_plane(self):
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            assert source_plane.coordinates == [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

        def test__four_coordinates_and_offset_centre__doesnt_change_coordinate_values(self):
            # The centre is used by SourcePlaneGeomtry, but doesn't change the input coordinate values
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

            source_plane = sp.SourcePlane(coordinates, centre=(0.5, 0.5))

            assert source_plane.coordinates == [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

    class TestCoordinatesToCentre(object):
        def test__source_plane_centre_zeros_by_default__no_shift(self):
            coordinates = (0.0, 0.0)

            source_plane = sp.SourcePlane(coordinates)

            coordinates_shift = source_plane.coordinates_to_centre(coordinates)

            assert coordinates_shift[0] == 0.0
            assert coordinates_shift[1] == 0.0

        def test__source_plane_centre_x_shift__x_shifts(self):
            coordinates = (0.0, 0.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.5, 0.0))

            coordinates_shift = source_plane.coordinates_to_centre(source_plane.coordinates)

            assert coordinates_shift[0] == -0.5
            assert coordinates_shift[1] == 0.0

        def test__source_plane_centre_y_shift__y_shifts(self):
            coordinates = (0.0, 0.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.5))

            coordinates_shift = source_plane.coordinates_to_centre(coordinates)

            assert coordinates_shift[0] == 0.0
            assert coordinates_shift[1] == -0.5

        def test__source_plane_centre_x_and_y_shift__x_and_y_both_shift(self):
            coordinates = (0.0, 0.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.5, 0.5))

            coordinates_shift = source_plane.coordinates_to_centre(coordinates)

            assert coordinates_shift[0] == -0.5
            assert coordinates_shift[1] == -0.5

        def test__source_plane_centre_and_coordinates__correct_shifts(self):
            coordinates = (0.2, 0.4)

            source_plane = sp.SourcePlane(coordinates, centre=(1.0, 0.5))

            coordinates_shift = source_plane.coordinates_to_centre(coordinates)

            assert coordinates_shift[0] == -0.8
            assert coordinates_shift[1] == pytest.approx(-0.1, 1e-5)

    class TestCoordinatesToRadius(object):
        def test__coordinates_overlap_source_plane_analysis__r_is_zero(self):
            coordinates = (0.0, 0.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            assert source_plane.coordinates_to_radius(coordinates) == 0.0

        def test__x_coordinates_is_one__r_is_one(self):
            coordinates = (1.0, 0.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            assert source_plane.coordinates_to_radius(coordinates) == 1.0

        def test__x_and_y_coordinates_are_one__r_is_root_two(self):
            coordinates = (1.0, 1.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            assert source_plane.coordinates_to_radius(coordinates) == pytest.approx(np.sqrt(2), 1e-5)

        def test__shift_x_coordinate_first__r_includes_shift(self):
            coordinates = (1.0, 0.0)

            source_plane = sp.SourcePlane(coordinates, centre=(-1.0, 0.0))

            assert source_plane.coordinates_to_radius(coordinates) == pytest.approx(2.0, 1e-5)

        def test__shift_x_and_y_coordinates_first__r_includes_shift(self):
            coordinates = (3.0, 3.0)

            source_plane = sp.SourcePlane(coordinates, centre=(2.0, 2.0))

            assert source_plane.coordinates_to_radius(coordinates) == pytest.approx(math.sqrt(2.0), 1e-5)

    class TestCoordinatesAngleFromX(object):
        def test__angle_is_zero__angles_follow_trig(self):
            coordinates = (1.0, 0.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            theta_from_x = source_plane.coordinates_angle_from_x(coordinates)

            assert theta_from_x == 0.0

        def test__angle_is_forty_five__angles_follow_trig(self):
            coordinates = (1.0, 1.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            theta_from_x = source_plane.coordinates_angle_from_x(coordinates)

            assert theta_from_x == 45.0

        def test__angle_is_sixty__angles_follow_trig(self):
            coordinates = (1.0, 1.7320)

            source_plane = sp.SourcePlane(coordinates)

            theta_from_x = source_plane.coordinates_angle_from_x(coordinates)

            assert theta_from_x == pytest.approx(60.0, 1e-3)

        def test__top_left_quandrant__angle_goes_above_90(self):
            coordinates = (-1.0, 1.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            theta_from_x = source_plane.coordinates_angle_from_x(coordinates)

            assert theta_from_x == 135.0

        def test__bottom_left_quandrant__angle_continues_above_180(self):
            coordinates = (-1.0, -1.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            theta_from_x = source_plane.coordinates_angle_from_x(coordinates)

            assert theta_from_x == 225.0

        def test__bottom_right_quandrant__angle_flips_back_to_above_90(self):
            coordinates = (1.0, -1.0)

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))

            theta_from_x = source_plane.coordinates_angle_from_x(coordinates)

            assert theta_from_x == 315.0

        def test__include_source_plane_centre__angle_takes_into_accounts(self):
            coordinates = (2.0, 2.0)

            source_plane = sp.SourcePlane(coordinates, centre=(1.0, 1.0))

            theta_from_x = source_plane.coordinates_angle_from_x(coordinates)

            assert theta_from_x == 45.0


class TestSorucePlaneBorder(object):
    class TestSetupBorder(object):

        def test__four_coordinates_in_circle__correct_border(self):
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

            border = sp.SourcePlaneBorder(coordinates, 3, centre=(0.0, 0.0))

            assert border.coordinates == [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
            assert border.radii == [1.0, 1.0, 1.0, 1.0]
            assert border.thetas == [0.0, 90.0, 180.0, 270.0]

        def test__six_coordinates_two_masked__correct_border(self):
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

            border = sp.SourcePlaneBorder(coordinates, 3, centre=(0.0, 0.0))

            assert border.coordinates == [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
            assert border.radii == [1.0, 1.0, 1.0, 1.0]
            assert border.thetas == [0.0, 90.0, 180.0, 270.0]

        def test__test_other_thetas_radii(self):
            coordinates = [(2.0, 0.0), (2.0, 2.0), (-1.0, -1.0), (0.0, -3.0)]

            border = sp.SourcePlaneBorder(coordinates, 3, centre=(0.0, 0.0))

            assert border.coordinates == [(2.0, 0.0), (2.0, 2.0), (-1.0, -1.0), (0.0, -3.0)]
            assert border.radii == [2.0, 2.0 * math.sqrt(2), math.sqrt(2.0), 3.0]
            assert border.thetas == [0.0, 45.0, 225.0, 270.0]

        def test__source_plane_centre_offset__coordinates_same_r_and_theta_shifted(self):
            coordinates = [(2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0)]

            border = sp.SourcePlaneBorder(coordinates, 3, centre=(1.0, 1.0))

            assert border.coordinates == [(2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0)]
            assert border.radii == [1.0, 1.0, 1.0, 1.0]
            assert border.thetas == [0.0, 90.0, 180.0, 270.0]

    class TestSetupBorderViaSourcePlaneAndMask(object):

        def test__four_coordinates_in_circle__correct_border(self):
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
            border_list = [0, 1, 2, 3]

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))
            border = source_plane.border_from_list_and_polynomial_degree(border_list, 3)

            assert border.coordinates == [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
            assert border.radii == [1.0, 1.0, 1.0, 1.0]
            assert border.thetas == [0.0, 90.0, 180.0, 270.0]

        def test__six_coordinates_two_masked__correct_border(self):
            coordinates = [(1.0, 0.0), (20., 20.), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0), (1.0, 1.0)]
            border_list = [0, 2, 3, 4]

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))
            border = source_plane.border_from_list_and_polynomial_degree(border_list, 3)

            assert border.coordinates == [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]
            assert border.radii == [1.0, 1.0, 1.0, 1.0]
            assert border.thetas == [0.0, 90.0, 180.0, 270.0]

        def test__test_other_thetas_radii(self):
            coordinates = [(2.0, 0.0), (20., 20.), (2.0, 2.0), (-1.0, -1.0), (0.0, -3.0), (1.0, 1.0)]
            border_list = [0, 2, 3, 4]

            source_plane = sp.SourcePlane(coordinates, centre=(0.0, 0.0))
            border = source_plane.border_from_list_and_polynomial_degree(border_list, 3)

            assert border.coordinates == [(2.0, 0.0), (2.0, 2.0), (-1.0, -1.0), (0.0, -3.0)]
            assert border.radii == [2.0, 2.0 * math.sqrt(2), math.sqrt(2.0), 3.0]
            assert border.thetas == [0.0, 45.0, 225.0, 270.0]

        def test__source_plane_centre_offset__coordinates_same_r_and_theta_shifted(self):
            coordinates = [(2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0)]
            border_list = [0, 1, 2, 3]

            source_plane = sp.SourcePlane(coordinates, centre=(1.0, 1.0))
            border = source_plane.border_from_list_and_polynomial_degree(border_list, 3)

            assert border.coordinates == [(2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0)]
            assert border.radii == [1.0, 1.0, 1.0, 1.0]
            assert border.thetas == [0.0, 90.0, 180.0, 270.0]

    class TestBorderPolynomial(object):
        def test__four_coordinates_in_circle__thetas_at_radius_are_each_coordinates_radius(self):
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0), (0.0, 0.0)]
            border_list = [0, 1, 2, 3]

            source_plane = sp.SourcePlane(coordinates)
            border = source_plane.border_from_list_and_polynomial_degree(border_list, 3)

            assert border.border_radius_at_theta(theta=0.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=90.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=180.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=270.0) == pytest.approx(1.0, 1e-3)

        def test__eight_coordinates_in_circle__thetas_at_each_coordinates_are_the_radius(self):
            coordinates = [(1.0, 0.0), (0.5 * math.sqrt(2), 0.5 * math.sqrt(2)), (0.0, 1.0),
                           (-0.5 * math.sqrt(2), 0.5 * math.sqrt(2)),
                           (-1.0, 0.0), (-0.5 * math.sqrt(2), -0.5 * math.sqrt(2)), (0.0, -1.0),
                           (0.5 * math.sqrt(2), -0.5 * math.sqrt(2))]

            border_list = [0, 1, 2, 3, 4, 5, 6, 7]

            source_plane = sp.SourcePlane(coordinates)
            border = source_plane.border_from_list_and_polynomial_degree(border_list, 3)

            assert border.border_radius_at_theta(theta=0.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=45.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=90.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=135.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=180.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=225.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=270.0) == pytest.approx(1.0, 1e-3)
            assert border.border_radius_at_theta(theta=315.0) == pytest.approx(1.0, 1e-3)

    class TestRelocateCoordinates(object):

        def test__outside_border_simple_cases__relocates_to_source_border(self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 32)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            source_border = sp.SourcePlaneBorder(circle, 3, centre=(0.0, 0.0))

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(2.5, 0.37))
            assert source_border.coordinates_to_radius(relocated_coordinate) == pytest.approx(1.0, 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(25.3, -9.2))
            assert source_border.coordinates_to_radius(relocated_coordinate) == pytest.approx(1.0, 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(13.5, 0.0))
            assert source_border.coordinates_to_radius(relocated_coordinate) == pytest.approx(1.0, 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(-2.5, -0.37))
            assert source_border.coordinates_to_radius(relocated_coordinate) == pytest.approx(1.0, 1e-3)

        def test__outside_border_simple_cases_2__relocates_to_source_border(self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 16)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            source_border = sp.SourcePlaneBorder(circle, 3, centre=(0.0, 0.0))

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(2.0, 0.0))
            assert relocated_coordinate == pytest.approx((1.0, 0.0), 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(1.0, 1.0))
            assert relocated_coordinate == pytest.approx((0.5 * math.sqrt(2), 0.5 * math.sqrt(2)), 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(0.0, 2.0))
            assert relocated_coordinate == pytest.approx((0.0, 1.0), 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(-1.0, 1.0))
            assert relocated_coordinate == pytest.approx((-0.5 * math.sqrt(2), 0.5 * math.sqrt(2)), 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(-2.0, 0.0))
            assert relocated_coordinate == pytest.approx((-1.0, 0.0), 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(-1.0, -1.0))
            assert relocated_coordinate == pytest.approx((-0.5 * math.sqrt(2), -0.5 * math.sqrt(2)), 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(0.0, -1.0))
            assert relocated_coordinate == pytest.approx((0.0, -1.0), 1e-3)

            relocated_coordinate = source_border.relocated_coordinate(coordinate=(1.0, -1.0))
            assert relocated_coordinate == pytest.approx((0.5 * math.sqrt(2), -0.5 * math.sqrt(2)), 1e-3)

        def test__outside_border_simple_cases_setup__via_source_plane_border_list_routine__relocates_to_source_border(
                self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 16)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            coordinates = circle + [(2.0, 0.0), (1.0, 1.0), (0.0, 2.0), (-1.0, 1.0),
                                    (-2.0, 0.0), (-1.0, -1.0), (0.0, -2.0), (1.0, -1.0)]

            border_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

            source_plane = sp.SourcePlane(coordinates)
            source_plane.relocate_coordinates_outside_border_from_list_and_polynomial_degree(border_list, 3)

            source_plane.coordinates = map(lambda r: pytest.approx(r, 1e-3), source_plane.coordinates)

            assert source_plane.coordinates[:][0:16] == coordinates[:][0:16]
            assert source_plane.coordinates[:][16] == (1.0, 0.0)
            assert source_plane.coordinates[:][17] == (0.5 * math.sqrt(2), 0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][18] == (0.0, 1.0)
            assert source_plane.coordinates[:][19] == (-0.5 * math.sqrt(2), 0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][20] == (-1.0, 0.0)
            assert source_plane.coordinates[:][21] == (-0.5 * math.sqrt(2), -0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][22] == (0.0, -1.0)
            assert source_plane.coordinates[:][23] == (0.5 * math.sqrt(2), -0.5 * math.sqrt(2))

        def test__outside_border_same_as_above_but_setup_via_border_list__relocates_to_source_border(self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 16)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            coordinates = circle + [(2.0, 0.0), (1.0, 1.0), (0.0, 2.0), (-1.0, 1.0),
                                    (-2.0, 0.0), (-1.0, -1.0), (0.0, -2.0), (1.0, -1.0)]

            border_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

            source_plane = sp.SourcePlane(coordinates)
            source_border = source_plane.border_from_list_and_polynomial_degree(border_list, 3)
            source_plane.relocate_coordinates_outside_border(source_border)

            source_plane.coordinates = map(lambda r: pytest.approx(r, 1e-3), source_plane.coordinates)

            assert source_plane.coordinates[:][0:16] == coordinates[:][0:16]
            assert source_plane.coordinates[:][16] == (1.0, 0.0)
            assert source_plane.coordinates[:][17] == (0.5 * math.sqrt(2), 0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][18] == (0.0, 1.0)
            assert source_plane.coordinates[:][19] == (-0.5 * math.sqrt(2), 0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][20] == (-1.0, 0.0)
            assert source_plane.coordinates[:][21] == (-0.5 * math.sqrt(2), -0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][22] == (0.0, -1.0)
            assert source_plane.coordinates[:][23] == (0.5 * math.sqrt(2), -0.5 * math.sqrt(2))

        def test__all_inside_border_simple_cases__no_relocations(self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 16)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            coordinates_original = circle + [(0.2, 0.0), (0.1, 0.1), (0.0, 0.2), (-0.1, 0.1),
                                             (-0.2, 0.0), (-0.1, -0.1), (0.0, -0.2), (0.1, -0.1)]

            border_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

            source_plane = sp.SourcePlane(coordinates_original)
            source_plane.relocate_coordinates_outside_border_from_list_and_polynomial_degree(border_list, 3)

            source_plane.coordinates = map(lambda r: pytest.approx(r, 1e-3), source_plane.coordinates)

            assert source_plane.coordinates == coordinates_original

        def test__inside_border_simple_cases_setup_via_border_list__no_relocations(self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 16)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            coordinates = circle + [(0.5, 0.0), (0.5, 0.5), (0.0, 0.5), (-0.5, 0.5),
                                    (-0.5, 0.0), (-0.5, -0.5), (0.0, -0.5), (0.5, -0.5)]

            border_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

            source_plane = sp.SourcePlane(coordinates)
            source_plane.relocate_coordinates_outside_border_from_list_and_polynomial_degree(border_list, 3)

            source_plane.coordinates = map(lambda r: pytest.approx(r, 1e-3), source_plane.coordinates)

            assert source_plane.coordinates[:][0:24] == coordinates[:][0:24]

        def test__inside_and_outside_border_simple_cases__changes_where_appropriate(self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 16)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            coordinates = circle + [(0.5, 0.0), (0.5, 0.5), (0.0, 0.5), (-0.5, 0.5),
                                    (-2.0, 0.0), (-1.0, -1.0), (0.0, -2.0), (1.0, -1.0)]

            border_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

            source_plane = sp.SourcePlane(coordinates)

            source_plane.relocate_coordinates_outside_border_from_list_and_polynomial_degree(border_list, 3)

            source_plane.coordinates = map(lambda r: pytest.approx(r, 1e-3), source_plane.coordinates)

            assert source_plane.coordinates[:][0:20] == coordinates[:][0:20]
            assert source_plane.coordinates[:][20] == (-1.0, 0.0)
            assert source_plane.coordinates[:][21] == (-0.5 * math.sqrt(2), -0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][22] == (0.0, -1.0)
            assert source_plane.coordinates[:][23] == (0.5 * math.sqrt(2), -0.5 * math.sqrt(2))

        def test__change_border_list__works_as_above(self):
            thetas = np.linspace(0.0, 2.0 * np.pi, 16)
            circle = list(map(lambda x: (np.cos(x), np.sin(x)), thetas))

            coordinates = [(-2.0, 0.0), (-1.0, -1.0), (0.0, -2.0), (1.0, -1.0)] + circle + \
                          [(0.5, 0.0), (0.5, 0.5), (0.0, 0.5), (-0.5, 0.5)]

            border_list = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

            source_plane = sp.SourcePlane(coordinates)

            source_plane.relocate_coordinates_outside_border_from_list_and_polynomial_degree(border_list, 3)

            source_plane.coordinates = map(lambda r: pytest.approx(r, 1e-3), source_plane.coordinates)

            assert source_plane.coordinates[:][0] == (-1.0, 0.0)
            assert source_plane.coordinates[:][1] == (-0.5 * math.sqrt(2), -0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][2] == (0.0, -1.0)
            assert source_plane.coordinates[:][3] == (0.5 * math.sqrt(2), -0.5 * math.sqrt(2))
            assert source_plane.coordinates[:][4:24] == coordinates[:][4:24]

    class TestMoveFactors(object):
        def test__inside_border__move_factor_is_1(self):
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

            source_border = sp.SourcePlaneBorder(coordinates, 3, centre=(0.0, 0.0))

            assert source_border.move_factor(coordinate=(0.5, 0.0)) == 1.0
            assert source_border.move_factor(coordinate=(-0.5, 0.0)) == 1.0
            assert source_border.move_factor(coordinate=(0.25, 0.25)) == 1.0
            assert source_border.move_factor(coordinate=(0.0, 0.0)) == 1.0

        def test__outside_border_double_its_radius__move_factor_is_05(self):
            coordinates = [(1.0, 0.0), (0.0, 1.0), (-1.0, 0.0), (0.0, -1.0)]

            source_border = sp.SourcePlaneBorder(coordinates, 3, centre=(0.0, 0.0))

            assert source_border.move_factor(coordinate=(2.0, 0.0)) == pytest.approx(0.5, 1e-3)
            assert source_border.move_factor(coordinate=(0.0, 2.0)) == pytest.approx(0.5, 1e-3)
            assert source_border.move_factor(coordinate=(-2.0, 0.0)) == pytest.approx(0.5, 1e-3)
            assert source_border.move_factor(coordinate=(0.0, -2.0)) == pytest.approx(0.5, 1e-3)

        def test__outside_border_double_its_radius_and_offset__move_factor_is_05(self):
            coordinates = [(2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0)]

            source_border = sp.SourcePlaneBorder(coordinates, 3, centre=(1.0, 1.0))

            assert source_border.move_factor(coordinate=(3.0, 1.0)) == pytest.approx(0.5, 1e-3)
            assert source_border.move_factor(coordinate=(1.0, 3.0)) == pytest.approx(0.5, 1e-3)
            assert source_border.move_factor(coordinate=(1.0, 3.0)) == pytest.approx(0.5, 1e-3)
            assert source_border.move_factor(coordinate=(3.0, 1.0)) == pytest.approx(0.5, 1e-3)


class TestRegularizationMatrix(object):

    # The regularization matrix, H, is calculated by defining a set of B matrices which describe how source-plane
    # pixels map to one another. For example, if we had a 3x3 square grid:

    # ______
    # |0|1|2|
    # |3|4|5|
    # |6|7|8|
    # ^^^^^^^

    # Lets say we want to regularize this grid so that each square pixel is regularized with a pixel to its right and
    # below it.

    # So, 0 is regularized with pixels 1 and 3, pixel 1 with 2 and 4, but pixel 2 with only pixel 5, etc. So,
    #
    # We make two 9 x 9 B matrices, which describe regularization in each direction. So for regularization to the
    # right of each pixel:

    # B_x = [-1,  1,  0,  0,  0,  0,  0,  0,  0] # [0->1] This, row 0, correspodns to pixel 0 (signified by the -1). The 1's in columns 1 is saying we want to regularize pixel 0 with pixel 1.
    #       [ 0, -1,  1,  0,  0,  0,  0,  0,  0] # [1->2] Row 1 for pixel 1 (again, the -1 tells us this), regularized with pixels 2.
    #       [ 0,  0, -1,  0,  0,  0,  0,  0,  0] # [] NOTE - pixel 2 is NOT regularized with pixel 3 (check the square grid)!
    #       [ 0,  0,  0, -1,  1,  0,  0,  0,  0] # [3->4]
    #       [ 0,  0,  0,  0, -1,  1,  0,  0,  0] # [4->5]
    #       [ 0,  0,  0,  0,  0, -1,  0,  0,  0] # [] NOTE - pixel 5 not regularized with pixel 6!
    #       [ 0,  0,  0,  0,  0,  0, -1,  1,  0] # [6->7]
    #       [ 0,  0,  0,  0,  0,  0,  0, -1,  1] # [7->8]
    #       [ 0,  0,  0,  0,  0,  0,  0,  0, -1] # [] NOTE - Not regularized with anything

    # We now make another B matrix for the regularization beneath each pixel:

    # B_y = [-1,  0,  0,  1,  0,  0,  0,  0,  0] # [0->3] This, row 0, correspodns to pixel 0 (signified by the -1). The 1's in columns 3 is saying we want to regularize pixel 0 with pixel 3.
    #       [ 0, -1,  0,  0,  1,  0,  0,  0,  0] # [1->4] Row 1 for pixel 1 (again, the -1 tells us this), regularized with pixel 4
    #       [ 0,  0, -1,  0,  0,  1,  0,  0,  0] # [2->5]
    #       [ 0,  0,  0, -1,  0,  0,  1,  0,  0] # [3->6]
    #       [ 0,  0,  0,  0, -1,  0,  0,  1,  0] # [4->7]
    #       [ 0,  0,  0,  0,  0, -1,  0,  0,  1] # [5->8]
    #       [ 0,  0,  0,  0,  0,  0, -1,  0,  0] # [] No regularized performed in these last 3 rows / pixels
    #       [ 0,  0,  0,  0,  0,  0,  0, -1,  0] # []
    #       [ 0,  0,  0,  0,  0,  0,  0,  0, -1] # []

    # So, we basically just make B matrices representing regularization in each direction. For each, we can then compute
    # their corresponding regularization matrix, H, as, H = B * B.T (matrix multiplication)

    # So, H_x = B_x.T, * B_x H_y = B_y.T * B_y
    # And our overall regularization matrix, H = H_x + H_y

    # For an adaptive Voronoi grid, we do the exact same thing, however we make a B matrix for every shared Voronoi vertex
    # of each soure-pixel cluster. This means that the number of B matrices we compute is equal to the the number of
    # Voronoi vertices in the source-pixel with the most Voronoi vertices (i.e. the most neighbours a source-pixel has).

    ### COMBINING B MATRICES ###

    # Whereas the examples above had each -1 going down the diagonal, this is not necessary. It valid to put each pairing
    # anywhere. So, if we had a 4x4 B matrix, where pixel 0 regularizes 1, 2 -> 3 and 3 -> 0, we can set this up
    # as one matrix even though the pixel 0 comes up twice!

    # B = [-1, 1, 0 ,0] # [0->1]
    #     [0, 0, 0 ,0] # We can skip rows by making them all zeros.
    #     [0, 0, -1 ,1] # [2->3]
    #     [1, 0, 0 ,-1] # [3->0] This is valid!

    # So, we don't have to make the same number of B matrices as Voronoi vertices, as we can combine them into a few B
    # matrices like this

    #### SKIPPING THE B MATRIX CALCULATION ####

    # The routine make_via_pixel_pairs doesn't use the B matrices to compute H at all!. They are used purely for testing.

    # This is because, if you know all the pairs between source pixels (which the Voronoi gridding can tell you), you
    # can bypass the B matrix multiplicaion entire and enter the values directly into the H matrix. Obviously, this saves
    # a huge amount of time and memory, but makes the routine hard to understand. Nevertheless, as the tests below confirm,
    # It produces a numerically equivalent result to the B matrices above.

    # It should be noted this routine is defined such that all pixels are regularized with one another (e.g. if 1->2,
    # then 2->1 as well). There are regularization schemes where this is not the case (i.e. 1->2 but not 2->1), however
    # For a constant regularization scheme this amounts to a scaling of the regularization coefficient. For a non-constant
    # shceme it wouldn't make sense to have directional regularization.

    #### WEIGHTED REGULARIZATION ####

    # The final thing we want to do is apply non-constant regularization. The idea here is that we given each source
    # pixel an 'effective regularization weight', instead of applying just one constant scheme overall. The AutoLens
    # paper motives why, but the idea is basically that different regions of the source-plane want different
    # levels of regularizations.

    # Say we have our regularization weights (see the code for how they are computed), how does this change our B matrix?
    # Well, we just multiple the regularization weight of each source-pixel by each row of B it has a -1 in, so:

    # regularization_weights = [1, 2, 3, 4]

    # B = [-1, 1, 0 ,0] # [0->1]
    #     [0, -2, 2 ,0] # [1->2]
    #     [0, 0, -3 ,3] # [2->3]
    #     [4, 0, 0 ,-4] # [3->0] This is valid!

    # If our -1's werent down the diagonal this would look like:

    # B = [4, 0, 0 ,-4] # [3->0]
    #     [0, -2, 2 ,0] # [1->2]
    #     [-1, 1, 0 ,0] # [0->1]
    #     [0, 0, -3 ,3] # [2->3] This is valid!

    # For the latter case, you can't just multiply regularization_weights by the matrix (as a vector). The pair routine
    # which computes H takes care of all of this :)

    def test__one_B_matrix_size_3x3__makes_correct_regularization_matrix(self):
        # Simple case, where we have just one regularization direction, regularizing pixel 0 -> 1 and 1 -> 2.

        # This means our B matrix is:

        # [-1, 1, 0]
        # [0, -1, 1]
        # [0, 0, -1]

        # Regularization Matrix, H = B * B.T.

        test_b_matrix = np.array([[-1, 1, 0],
                                  [1, -1, 0],
                                  [0, 0, 0]])

        test_regularization_matrix = np.matmul(test_b_matrix.T, test_b_matrix)

        no_verticies = np.array([1, 1, 0])
        pixel_pairs = np.array([[0, 1]])
        regularization_weights = np.ones((3))

        regularization_matrix = sp.RegularizationMatrix(3, regularization_weights, no_verticies, pixel_pairs)
        assert (regularization_matrix == test_regularization_matrix).all()

    def test__one_B_matrix_size_4x4__makes_correct_regularization_matrix(self):
        test_b_matrix = np.array([[-1, 0, 1, 0],
                                  [0, -1, 0, 1],
                                  [1, 0, -1, 0],
                                  [0, 1, 0, -1]])

        test_regularization_matrix = np.matmul(test_b_matrix.T, test_b_matrix)

        no_verticies = np.array([1, 1, 1, 1])
        pixel_pairs = np.array([[0, 2], [1, 3]])
        regularization_weights = np.ones((4))

        regularization_matrix = sp.RegularizationMatrix(4, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()

    def test__two_B_matrices_size_4x4__makes_correct_regularization_matrix(self):
        test_b_matrix_1 = np.array([[-1, 1, 0, 0],
                                    [0, -1, 1, 0],
                                    [0, 0, -1, 1],
                                    [1, 0, 0, -1]])

        test_regularization_matrix_1 = np.matmul(test_b_matrix_1.T, test_b_matrix_1)

        test_b_matrix_2 = np.array([[-1, 0, 0, 1],
                                    [1, -1, 0, 0],
                                    [0, 1, -1, 0],
                                    [0, 0, 1, -1]])

        test_regularization_matrix_2 = np.matmul(test_b_matrix_2.T, test_b_matrix_2)

        test_regularization_matrix = test_regularization_matrix_1 + test_regularization_matrix_2

        no_verticies = np.array([2, 2, 2, 2])
        pixel_pairs = np.array([[0, 1], [1, 2], [2, 3], [3, 0]])
        regularization_weights = np.ones((4))

        regularization_matrix = sp.RegularizationMatrix(4, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()

    def test__two_B_matrices_size_4x4__makes_correct_regularization_matrix2(self):
        test_b_matrix_1 = np.matrix([[-1, 0, 1, 0],
                                     [0, -1, 1, 0],
                                     [1, 0, -1, 0],
                                     [1, 0, 0, -1]])

        test_regularization_matrix_1 = np.matmul(test_b_matrix_1.T, test_b_matrix_1)

        test_b_matrix_2 = np.matrix([[-1, 0, 0, 1],
                                     [0, 0, 0, 0],
                                     [0, 1, -1, 0],
                                     [0, 0, 0, 0]])

        test_regularization_matrix_2 = np.matmul(test_b_matrix_2.T, test_b_matrix_2)

        test_regularization_matrix = test_regularization_matrix_1 + test_regularization_matrix_2

        no_verticies = np.array([2, 1, 2, 1])
        pixel_pairs = np.array([[0, 2], [1, 2], [0, 3]])
        regularization_weights = np.ones((4))

        regularization_matrix = sp.RegularizationMatrix(4, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()

    def test__two_pairs_two_B_matrices_size_3x3__makes_correct_regularization_matrix(self):
        # Here, we define the pixel_pairs first here and make the B matrices based on them.

        # You'll notice that actually, the B Matrix doesn't have to have the -1's going down the diagonal and we don't
        # have to have as many B matrices as we do the source pixel with the most Voronoi vertices. We can combine the
        # rows of each B matrix wherever we like ;0.

        pixel_pairs = np.array([[0, 1], [0, 2]])
        no_verticies = np.array([2, 1, 1])

        test_b_matrix_1 = np.array([[-1, 1, 0],  # Pair 1
                                    [-1, 0, 1],  # Pair 2
                                    [1, -1, 0]])  # Pair 1 flip

        test_regularization_matrix_1 = np.matmul(test_b_matrix_1.T, test_b_matrix_1)

        test_b_matrix_2 = np.array([[1, 0, -1],  # Pair 2 flip
                                    [0, 0, 0],
                                    [0, 0, 0]])

        test_regularization_matrix_2 = np.matmul(test_b_matrix_2.T, test_b_matrix_2)

        test_regularization_matrix = test_regularization_matrix_1 + test_regularization_matrix_2

        regularization_weights = np.ones((3))

        regularization_matrix = sp.RegularizationMatrix(3, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()

    def test__eight_pairs_four_B_matrices_size_6x6__makes_correct_regularization_matrix(self):
        # Again, lets exploit the freedom we have when setting up our B matrices to make matching it to pairs a lot less
        # Stressful.

        pixel_pairs = np.array([[0, 2], [1, 2], [0, 3], [4, 5], [1, 5], [0, 4], [2, 3], [2, 5]])

        no_verticies = np.array([3, 2, 4, 2, 2, 3])

        test_b_matrix_1 = np.array([[-1, 0, 1, 0, 0, 0],  # Pair 1
                                    [0, -1, 1, 0, 0, 0],  # Pair 2
                                    [-1, 0, 0, 1, 0, 0],  # Pair 3
                                    [0, 0, 0, 0, -1, 1],  # Pair 4
                                    [0, -1, 0, 0, 0, 1],  # Pair 5
                                    [-1, 0, 0, 0, 1, 0]])  # Pair 6

        test_regularization_matrix_1 = np.matmul(test_b_matrix_1.T, test_b_matrix_1)

        test_b_matrix_2 = np.array([[0, 0, -1, 1, 0, 0],  # Pair 7
                                    [0, 0, -1, 0, 0, 1],  # Pair 8
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0]])

        test_regularization_matrix_2 = np.matmul(test_b_matrix_2.T, test_b_matrix_2)

        test_b_matrix_3 = np.array([[1, 0, -1, 0, 0, 0],  # Pair 1 flip
                                    [0, 1, -1, 0, 0, 0],  # Pair 2 flip
                                    [1, 0, 0, -1, 0, 0],  # Pair 3 flip
                                    [0, 0, 0, 0, 1, -1],  # Pair 4 flip
                                    [0, 1, 0, 0, 0, -1],  # Pair 5 flip
                                    [1, 0, 0, 0, -1, 0]])  # Pair 6 flip

        test_regularization_matrix_3 = np.matmul(test_b_matrix_3.T, test_b_matrix_3)

        test_b_matrix_4 = np.array([[0, 0, 1, -1, 0, 0],  # Pair 7 flip
                                    [0, 0, 1, 0, 0, -1],  # Pair 8 flip
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0]])

        test_regularization_matrix_4 = np.matmul(test_b_matrix_4.T, test_b_matrix_4)

        test_regularization_matrix = test_regularization_matrix_1 + test_regularization_matrix_2 + \
                                     test_regularization_matrix_3 + + test_regularization_matrix_4

        regularization_weights = np.ones((6))

        regularization_matrix = sp.RegularizationMatrix(6, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()

    def test__one_B_matrix_size_3x3_variables_regularization_weights__makes_correct_regularization_matrix(self):
        # Simple case, where we have just one regularization direction, regularizing pixel 0 -> 1 and 1 -> 2.

        # This means our B matrix is:

        # [-1, 1, 0]
        # [0, -1, 1]
        # [0, 0, -1]

        # Regularization Matrix, H = B * B.T.I can

        regularization_weights = np.array([2.0, 4.0, 1.0])

        test_b_matrix = np.array([[-1, 1, 0],  # [[-2, 2, 0], (Matrix)
                                  [1, -1, 0],  # [4, -4, 0], (after)
                                  [0, 0, 0]])  # [0, 0,  0]]) (weights)

        test_b_matrix = (test_b_matrix.T * regularization_weights).T

        test_regularization_matrix = np.matmul(test_b_matrix.T, test_b_matrix)

        no_verticies = np.array([1, 1, 0])
        pixel_pairs = np.array([[0, 1]])

        regularization_matrix = sp.RegularizationMatrix(3, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()

    def test__two_B_matrices_size_4x4_variables_regularization_weights__makes_correct_regularization_matrix(self):
        # Simple case, where we have just one regularization direction, regularizing pixel 0 -> 1 and 1 -> 2.

        # This means our B matrix is:

        # [-1, 1, 0]
        # [0, -1, 1]
        # [0, 0, -1]

        # Regularization Matrix, H = B * B.T.I can

        regularization_weights = np.array([2.0, 4.0, 1.0, 8.0])

        test_b_matrix_1 = np.array([[-2, 2, 0, 0],
                                    [-2, 0, 2, 0],
                                    [0, -4, 4, 0],
                                    [0, -4, 0, 4]])

        test_b_matrix_2 = np.array([[4, -4, 0, 0],
                                    [1, 0, -1, 0],
                                    [0, 1, -1, 0],
                                    [0, 8, 0, -8]])

        test_regularization_matrix_1 = np.matmul(test_b_matrix_1.T, test_b_matrix_1)
        test_regularization_matrix_2 = np.matmul(test_b_matrix_2.T, test_b_matrix_2)

        test_regularization_matrix = test_regularization_matrix_1 + test_regularization_matrix_2

        no_verticies = np.array([2, 3, 2, 1])
        pixel_pairs = np.array([[0, 1], [0, 2], [1, 2], [1, 3]])

        regularization_matrix = sp.RegularizationMatrix(4, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()

    def test__four_B_matrices_size_6x6_with_regularization_weights__makes_correct_regularization_matrix(self):
        pixel_pairs = np.array([[0, 1], [0, 4], [1, 2], [1, 4], [2, 3], [2, 4], [2, 5], [3, 5], [4, 5]])
        no_verticies = np.array([2, 3, 4, 2, 4, 3])
        regularization_weights = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

        # I'm inputting the regularizationo weights directly thiss time, as it'd be a pain to multiply with a loop.

        test_b_matrix_1 = np.array([[-1, 1, 0, 0, 0, 0],  # Pair 1
                                    [-1, 0, 0, 0, 1, 0],  # Pair 2
                                    [0, -2, 2, 0, 0, 0],  # Pair 3
                                    [0, -2, 0, 0, 2, 0],  # Pair 4
                                    [0, 0, -3, 3, 0, 0],  # Pair 5
                                    [0, 0, -3, 0, 3, 0]])  # Pair 6

        test_b_matrix_2 = np.array([[0, 0, -3, 0, 0, 3],  # Pair 7
                                    [0, 0, 0, -4, 0, 4],  # Pair 8
                                    [0, 0, 0, 0, -5, 5],  # Pair 9
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0]])

        # Now do the same pairs but with the regularization direction and weights swapped.

        test_b_matrix_3 = np.array([[2, -2, 0, 0, 0, 0],  # Pair 1
                                    [5, 0, 0, 0, -5, 0],  # Pair 2
                                    [0, 3, -3, 0, 0, 0],  # Pair 3
                                    [0, 5, 0, 0, -5, 0],  # Pair 4
                                    [0, 0, 4, -4, 0, 0],  # Pair 5
                                    [0, 0, 5, 0, -5, 0]])  # Pair 6

        test_b_matrix_4 = np.array([[0, 0, 6, 0, 0, -6],  # Pair 7
                                    [0, 0, 0, 6, 0, -6],  # Pair 8
                                    [0, 0, 0, 0, 6, -6],  # Pair 9
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0]])

        test_regularization_matrix_1 = np.matmul(test_b_matrix_1.T, test_b_matrix_1)
        test_regularization_matrix_2 = np.matmul(test_b_matrix_2.T, test_b_matrix_2)
        test_regularization_matrix_3 = np.matmul(test_b_matrix_3.T, test_b_matrix_3)
        test_regularization_matrix_4 = np.matmul(test_b_matrix_4.T, test_b_matrix_4)

        test_regularization_matrix = test_regularization_matrix_1 + test_regularization_matrix_2 + \
                                     test_regularization_matrix_3 + test_regularization_matrix_4

        regularization_matrix = sp.RegularizationMatrix(6, regularization_weights, no_verticies, pixel_pairs)

        assert (regularization_matrix == test_regularization_matrix).all()


class TestKMeans:

    def test__simple_points__sets_up_two_clusters(self):
        sparse_coordinates = np.array([[0.99, 0.99], [1.0, 1.0], [1.01, 1.01],
                                       [1.99, 1.99], [2.0, 2.0], [2.01, 2.01]])

        kmeans = sp.KMeans(sparse_coordinates, n_clusters=2)

        kmeans.cluster_centers_ = list(map(lambda x: list(x), kmeans.cluster_centers_))

        assert [2.0, 2.0] in kmeans.cluster_centers_
        assert [1.0, 1.0] in kmeans.cluster_centers_

        assert list(kmeans.labels_).count(0) == 3
        assert list(kmeans.labels_).count(1) == 3

    def test__simple_points__sets_up_three_clusters(self):
        sparse_coordinates = np.array([[-0.99, -0.99], [-1.0, -1.0], [-1.01, -1.01],
                                       [0.99, 0.99], [1.0, 1.0], [1.01, 1.01],
                                       [1.99, 1.99], [2.0, 2.0], [2.01, 2.01]])

        kmeans = sp.KMeans(sparse_coordinates, n_clusters=3)

        kmeans.cluster_centers_ = list(map(lambda x: list(x), kmeans.cluster_centers_))

        assert [2.0, 2.0] in kmeans.cluster_centers_
        assert [1.0, 1.0] in kmeans.cluster_centers_
        assert [-1.0, -1.0] in kmeans.cluster_centers_

        assert list(kmeans.labels_).count(0) == 3
        assert list(kmeans.labels_).count(1) == 3
        assert list(kmeans.labels_).count(2) == 3

    def test__simple_points__sets_up_three_clusters_more_points_in_third_cluster(self):
        sparse_coordinates = np.array([[-0.99, -0.99], [-1.0, -1.0], [-1.01, -1.01],

                                       [0.99, 0.99], [1.0, 1.0], [1.01, 1.01],
                                       [0.99, 0.99], [1.0, 1.0], [1.01, 1.01],

                                       [1.99, 1.99], [2.0, 2.0], [2.01, 2.01],
                                       [1.99, 1.99], [2.0, 2.0], [2.01, 2.01],
                                       [1.99, 1.99], [2.0, 2.0], [2.01, 2.01],
                                       [1.99, 1.99], [2.0, 2.0], [2.01, 2.01]])

        kmeans = sp.KMeans(sparse_coordinates, n_clusters=3)

        kmeans.cluster_centers_ = list(map(lambda x: pytest.approx(list(x), 1e-3), kmeans.cluster_centers_))

        assert [2.0, 2.0] in kmeans.cluster_centers_
        assert [1.0, 1.0] in kmeans.cluster_centers_
        assert [-1.0, -1.0] in kmeans.cluster_centers_

        assert list(kmeans.labels_).count(0) == 3 or 6 or 12
        assert list(kmeans.labels_).count(1) == 3 or 6 or 12
        assert list(kmeans.labels_).count(2) == 3 or 6 or 12

        assert list(kmeans.labels_).count(0) != list(kmeans.labels_).count(1) != list(kmeans.labels_).count(2)


class TestVoronoi:

    def test__points_in_x_cross_shape__sets_up_diamond_voronoi_vertices(self):
        # 5 points in the shape of the face of a 5 on a die - makes a diamond Voronoi diagram

        points = np.array([[-1.0, 1.0], [1.0, 1.0],
                           [0.0, 0.0],
                           [-1.0, -1.0], [1.0, -1.0]])

        voronoi = sp.Voronoi(points)

        voronoi.vertices = list(map(lambda x: list(x), voronoi.vertices))

        assert [0, 1.] in voronoi.vertices
        assert [-1., 0.] in voronoi.vertices
        assert [1., 0.] in voronoi.vertices
        assert [0., -1.] in voronoi.vertices

    def test__9_points_in_square___sets_up_square_of_voronoi_vertices(self):
        # 9 points in a square - makes a square (this is the example int he scipy documentaiton page)

        points = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
                           [0.0, 1.0], [1.0, 1.0], [2.0, 1.0],
                           [0.0, 2.0], [1.0, 2.0], [2.0, 2.0]])

        voronoi = sp.Voronoi(points)

        # ridge points is a numpy array for speed, but convert to list for the comparisons below so we can use in
        # to look for each list

        voronoi.vertices = list(map(lambda x: list(x), voronoi.vertices))

        assert [0.5, 1.5] in voronoi.vertices
        assert [1.5, 0.5] in voronoi.vertices
        assert [0.5, 0.5] in voronoi.vertices
        assert [1.5, 1.5] in voronoi.vertices

    def test__points_in_x_cross_shape__sets_up_pairs_of_voronoi_cells(self):
        # 5 points in the shape of the face of a 5 on a die - makes a diamond Voronoi diagram

        points = np.array([[-1.0, 1.0], [1.0, 1.0],
                           [0.0, 0.0],
                           [-1.0, -1.0], [1.0, -1.0]])

        voronoi = sp.Voronoi(points)

        # ridge points is a numpy array for speed, but convert to list for the comparisons below so we can use in
        # to look for each list

        voronoi.ridge_points = list(map(lambda x: list(x), voronoi.ridge_points))

        assert len(voronoi.ridge_points) == 8

        assert [2, 0] in voronoi.ridge_points or [0, 2] in voronoi.ridge_points
        assert [2, 1] in voronoi.ridge_points or [1, 2] in voronoi.ridge_points
        assert [2, 3] in voronoi.ridge_points or [3, 2] in voronoi.ridge_points
        assert [2, 4] in voronoi.ridge_points or [4, 2] in voronoi.ridge_points
        assert [0, 1] in voronoi.ridge_points or [1, 0] in voronoi.ridge_points
        assert [0.3] in voronoi.ridge_points or [3, 0] in voronoi.ridge_points
        assert [3, 4] in voronoi.ridge_points or [4, 3] in voronoi.ridge_points
        assert [4, 1] in voronoi.ridge_points or [1, 4] in voronoi.ridge_points

    def test__9_points_in_square___sets_up_pairs_of_voronoi_cells(self):
        # 9 points in a square - makes a square (this is the example int he scipy documentaiton page)

        points = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
                           [0.0, 1.0], [1.0, 1.0], [2.0, 1.0],
                           [0.0, 2.0], [1.0, 2.0], [2.0, 2.0]])

        voronoi = sp.Voronoi(points)

        # ridge points is a numpy array for speed, but convert to list for the comparisons below so we can use in
        # to look for each list

        voronoi.ridge_points = list(map(lambda x: list(x), voronoi.ridge_points))

        assert len(voronoi.ridge_points) == 12

        assert [0, 1] in voronoi.ridge_points or [1, 0] in voronoi.ridge_points
        assert [1, 2] in voronoi.ridge_points or [2, 1] in voronoi.ridge_points
        assert [3, 4] in voronoi.ridge_points or [4, 3] in voronoi.ridge_points
        assert [4, 5] in voronoi.ridge_points or [5, 4] in voronoi.ridge_points
        assert [6, 7] in voronoi.ridge_points or [7, 6] in voronoi.ridge_points
        assert [7, 8] in voronoi.ridge_points or [8, 7] in voronoi.ridge_points

        assert [0, 3] in voronoi.ridge_points or [3, 0] in voronoi.ridge_points
        assert [1, 4] in voronoi.ridge_points or [4, 1] in voronoi.ridge_points
        assert [4, 7] in voronoi.ridge_points or [7, 4] in voronoi.ridge_points
        assert [2, 5] in voronoi.ridge_points or [5, 2] in voronoi.ridge_points
        assert [5, 8] in voronoi.ridge_points or [8, 5] in voronoi.ridge_points
        assert [3, 6] in voronoi.ridge_points or [6, 3] in voronoi.ridge_points

    def test__points_in_x_cross_shape__neighbors_of_each_source_pixel_correct(self):
        # 5 points in the shape of the face of a 5 on a die - makes a diamond Voronoi diagram

        points = np.array([[-1.0, 1.0], [1.0, 1.0],
                           [0.0, 0.0],
                           [-1.0, -1.0], [1.0, -1.0]])

        voronoi = sp.Voronoi(points)

        assert voronoi.neighbors_total[0] == 3
        assert voronoi.neighbors_total[1] == 3
        assert voronoi.neighbors_total[2] == 4
        assert voronoi.neighbors_total[3] == 3
        assert voronoi.neighbors_total[4] == 3

        assert set(voronoi.neighbors[0]) == set([2, 1, 3])
        assert set(voronoi.neighbors[1]) == set([2, 0, 4])
        assert set(voronoi.neighbors[2]) == set([0, 1, 3, 4])
        assert set(voronoi.neighbors[3]) == set([2, 0, 4])
        assert set(voronoi.neighbors[4]) == set([2, 1, 3])

    def test__9_points_in_square___neighbors_of_each_source_pixel_correct(self):
        # 9 points in a square - makes a square (this is the example int he scipy documentaiton page)

        points = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
                           [0.0, 1.0], [1.0, 1.0], [2.0, 1.0],
                           [0.0, 2.0], [1.0, 2.0], [2.0, 2.0]])

        voronoi = sp.Voronoi(points)

        assert voronoi.neighbors_total[0] == 2
        assert voronoi.neighbors_total[1] == 3
        assert voronoi.neighbors_total[2] == 2
        assert voronoi.neighbors_total[3] == 3
        assert voronoi.neighbors_total[4] == 4
        assert voronoi.neighbors_total[5] == 3
        assert voronoi.neighbors_total[6] == 2
        assert voronoi.neighbors_total[7] == 3
        assert voronoi.neighbors_total[8] == 2

        assert set(voronoi.neighbors[0]) == set([1, 3])
        assert set(voronoi.neighbors[1]) == set([0, 2, 4])
        assert set(voronoi.neighbors[2]) == set([1, 5])
        assert set(voronoi.neighbors[3]) == set([0, 4, 6])
        assert set(voronoi.neighbors[4]) == set([1, 3, 5, 7])
        assert set(voronoi.neighbors[5]) == set([2, 4, 8])
        assert set(voronoi.neighbors[6]) == set([3, 7])
        assert set(voronoi.neighbors[7]) == set([4, 6, 8])
        assert set(voronoi.neighbors[8]) == set([5, 7])


class TestMatchCoordinatesFromClusters:

    def test__sub_coordinates_to_source_pixels_via_nearest_neighbour__case1__correct_pairs(self):
        source_pixels = np.array([[1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0], [1.0, -1.0]])
        sub_coordinates = np.array([[1.1, 1.1], [-1.1, 1.1], [-1.1, -1.1], [1.1, -1.1]])

        sub_image_pixel_to_source_pixel_index = sp.sub_coordinates_to_source_pixels_via_nearest_neighbour(
            sub_coordinates,
            source_pixels)

        assert sub_image_pixel_to_source_pixel_index[0] == 0
        assert sub_image_pixel_to_source_pixel_index[1] == 1
        assert sub_image_pixel_to_source_pixel_index[2] == 2
        assert sub_image_pixel_to_source_pixel_index[3] == 3

    def test__sub_coordinates_to_source_pixels_via_nearest_neighbour___case2__correct_pairs(self):
        source_pixels = np.array([[1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0], [1.0, -1.0]])

        sub_coordinates = np.array([[1.1, 1.1], [-1.1, 1.1], [-1.1, -1.1], [1.1, -1.1],
                                    [0.9, -0.9], [-0.9, -0.9], [-0.9, 0.9], [0.9, 0.9]])

        sub_image_pixel_to_source_pixel_index = sp.sub_coordinates_to_source_pixels_via_nearest_neighbour(
            sub_coordinates,
            source_pixels)

        assert sub_image_pixel_to_source_pixel_index[0] == 0
        assert sub_image_pixel_to_source_pixel_index[1] == 1
        assert sub_image_pixel_to_source_pixel_index[2] == 2
        assert sub_image_pixel_to_source_pixel_index[3] == 3
        assert sub_image_pixel_to_source_pixel_index[4] == 3
        assert sub_image_pixel_to_source_pixel_index[5] == 2
        assert sub_image_pixel_to_source_pixel_index[6] == 1
        assert sub_image_pixel_to_source_pixel_index[7] == 0

    def test__sub_coordinates_to_source_pixels_via_nearest_neighbour___case3__correct_pairs(self):
        source_pixels = np.array([[1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0], [1.0, -1.0], [0.0, 0.0], [2.0, 2.0]])

        sub_coordinates = np.array([[0.1, 0.1], [-0.1, -0.1], [0.49, 0.49], [0.51, 0.51], [1.01, 1.01], [1.51, 1.51]])

        sub_image_pixel_to_source_pixel_index = sp.sub_coordinates_to_source_pixels_via_nearest_neighbour(
            sub_coordinates,
            source_pixels)

        assert sub_image_pixel_to_source_pixel_index[0] == 4
        assert sub_image_pixel_to_source_pixel_index[1] == 4
        assert sub_image_pixel_to_source_pixel_index[2] == 4
        assert sub_image_pixel_to_source_pixel_index[3] == 0
        assert sub_image_pixel_to_source_pixel_index[4] == 0
        assert sub_image_pixel_to_source_pixel_index[5] == 5

    def test__find_index_of_nearest_sparse_coordinate__simple_values(self):
        sub_coordinate_to_sparse_coordinate_index = [0, 3, 2, 5, 1, 4]

        assert sp.find_nearest_sparse_coordinate(0, sub_coordinate_to_sparse_coordinate_index) == 0
        assert sp.find_nearest_sparse_coordinate(1, sub_coordinate_to_sparse_coordinate_index) == 3
        assert sp.find_nearest_sparse_coordinate(2, sub_coordinate_to_sparse_coordinate_index) == 2
        assert sp.find_nearest_sparse_coordinate(3, sub_coordinate_to_sparse_coordinate_index) == 5
        assert sp.find_nearest_sparse_coordinate(4, sub_coordinate_to_sparse_coordinate_index) == 1
        assert sp.find_nearest_sparse_coordinate(5, sub_coordinate_to_sparse_coordinate_index) == 4

    def test__find_index_of_nearest_sparse_source_pixel__simple_values(self):
        source_pixel_to_sparse_source_pixel_index = [0, 3, 2, 5, 1, 4]

        assert sp.find_nearest_sparse_source_pixel(0, source_pixel_to_sparse_source_pixel_index) == 0
        assert sp.find_nearest_sparse_source_pixel(1, source_pixel_to_sparse_source_pixel_index) == 3
        assert sp.find_nearest_sparse_source_pixel(2, source_pixel_to_sparse_source_pixel_index) == 2
        assert sp.find_nearest_sparse_source_pixel(3, source_pixel_to_sparse_source_pixel_index) == 5
        assert sp.find_nearest_sparse_source_pixel(4, source_pixel_to_sparse_source_pixel_index) == 1
        assert sp.find_nearest_sparse_source_pixel(5, source_pixel_to_sparse_source_pixel_index) == 4

    def test__find_separation_of_coordinate_and_nearest_sparse_source_pixel__simple_values(self):
        source_pixel_centers = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]

        sub_coordinate = [1.5, 0.0]

        nearest_sparse_source_pixel_index = 0

        separation0 = sp.find_separation_of_sub_coordinate_and_nearest_sparse_source_pixel(source_pixel_centers,
                                                                                           sub_coordinate,
                                                                                           nearest_sparse_source_pixel_index)

        nearest_sparse_source_pixel_index = 1

        separation1 = sp.find_separation_of_sub_coordinate_and_nearest_sparse_source_pixel(source_pixel_centers,
                                                                                           sub_coordinate,
                                                                                           nearest_sparse_source_pixel_index)

        nearest_sparse_source_pixel_index = 2

        separation2 = sp.find_separation_of_sub_coordinate_and_nearest_sparse_source_pixel(source_pixel_centers,
                                                                                           sub_coordinate,
                                                                                           nearest_sparse_source_pixel_index)

        assert separation0 == 1.5 ** 2
        assert separation1 == 0.5 ** 2
        assert separation2 == 0.5 ** 2

    def test__find_separation_and_index_of_nearest_neighboring_source_pixel__simple_case(self):
        sub_coordinate = np.array([0.0, 0.0])
        source_pixel_centers = np.array([[0.0, 0.0], [-1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, -0.5]])

        # Lets assume we're currently on source_pixel 0 and all other source_pixels are neighbors

        source_pixel_neighbors = [1, 2, 3, 4]

        index, separation = sp.find_separation_and_nearest_neighboring_source_pixel(sub_coordinate,
                                                                                    source_pixel_centers,
                                                                                    source_pixel_neighbors)

        assert separation == (-0.5) ** 2
        assert index == 4

    def test__find_separation_and_index_of_nearest_neighboring_source_pixel__skips_if_not_a_neighbor(self):
        sub_coordinate = np.array([0.0, 0.0])
        source_pixel_centers = np.array([[0.0, 0.0], [-1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, -0.5], [0.0, -0.01]])

        # Lets assume we're currently on source_pixel 0 and the new source_pixel added above is not a neighbor (this doesn't make
        # sense geometrically, but tests the code functionality).

        source_pixel_neighbors = [1, 2, 3, 4]

        index, separation = sp.find_separation_and_nearest_neighboring_source_pixel(sub_coordinate,
                                                                                    source_pixel_centers,
                                                                                    source_pixel_neighbors)

        assert separation == (-0.5) ** 2
        assert index == 4

    def test__sub_coordinates_to_source_pixels_via_sparse_pairs__source_pixels_in_x_shape__correct_pairs(self):
        source_pixels = np.array([[-1.0, 1.0], [1.0, 1.0],
                                  [0.0, 0.0],
                                  [-1.0, -1.0], [1.0, -1.0]])

        # Make it so the central top, left, right and bottom coordinate all pair with the central source_pixel (index=2)

        sub_coordinates = np.array([[-1.0, 1.0], [0.0, 0.2], [1.0, 1.0],
                                    [-1.0, 0.2], [0.0, 0.0], [0.2, 0.0],
                                    [-1.0, -1.0], [0.0, -0.2], [1.0, -1.0]])

        voronoi = sp.Voronoi(source_pixels)

        sub_image_pixel_to_source_pixel_index_nearest_neighbour = sp.sub_coordinates_to_source_pixels_via_nearest_neighbour(
            sub_coordinates,
            source_pixels)

        # The sparse coordinates are not required by the pairing routine routine below, but included here for clarity
        sparse_coordinates = np.array([[0.1, 1.1], [0.0, 0.0], [0.1, -1.1]])

        coordinate_to_sparse_coordinate_index = np.array([0, 1, 0, 1, 1, 1, 2, 1, 2])
        sparse_coordinate_to_source_pixel_index = np.array([1, 2, 4])

        sub_image_pixel_to_source_pixel_index_sparse_pairs = sp.sub_coordinates_to_source_pixels_via_sparse_pairs(
            sub_coordinates,
            source_pixels, voronoi.neighbors,
            coordinate_to_sparse_coordinate_index,
            sparse_coordinate_to_source_pixel_index)

        assert sub_image_pixel_to_source_pixel_index_nearest_neighbour == sub_image_pixel_to_source_pixel_index_sparse_pairs

    def test__sub_coordinates_to_source_pixels_via_sparse_pairs__grid_of_source_pixels__correct_pairs(self):
        source_pixels = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
                                  [0.0, 1.0], [1.0, 1.0], [2.0, 1.0],
                                  [0.0, 2.0], [1.0, 2.0], [2.0, 2.0]])

        sub_coordinates = np.array([[0.0, 0.0], [1.0, 0.0], [2.0, 0.0],
                                    [0.0, 1.0], [1.0, 1.0], [2.0, 1.0],
                                    [0.0, 2.0], [1.0, 2.0], [2.0, 2.0]])

        voronoi = sp.Voronoi(source_pixels)

        sub_image_pixel_to_source_pixel_index_nearest_neighbour = sp.sub_coordinates_to_source_pixels_via_nearest_neighbour(
            sub_coordinates,
            source_pixels)

        # The sparse coordinates are not required by the pairing routine routine below, but included here for clarity
        sparse_coordinates = np.array([[0.0, 1.0], [1.0, 1.0], [2.0, 1.0]])

        sub_coordinate_to_sparse_coordinate_index = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2])
        sparse_coordinate_to_source_pixel_index = np.array([3, 4, 5])

        sub_image_pixel_to_source_pixel_index_sparse_pairs = sp.sub_coordinates_to_source_pixels_via_sparse_pairs(
            sub_coordinates,
            source_pixels, voronoi.neighbors,
            sub_coordinate_to_sparse_coordinate_index,
            sparse_coordinate_to_source_pixel_index)

        assert sub_image_pixel_to_source_pixel_index_nearest_neighbour == sub_image_pixel_to_source_pixel_index_sparse_pairs