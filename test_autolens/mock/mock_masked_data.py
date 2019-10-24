import numpy as np

class MockMaskedImaging(object):
    def __init__(self, imaging, mask, grid, blurring_grid, convolver):

        self.imaging = imaging
        self.mask = mask

        self.psf = imaging.psf

        self.grid = grid
        self.blurring_grid = blurring_grid
        self.convolver = convolver

        self.image = mask.mapping.array_from_array_2d(array_2d=imaging.image.in_2d)
        self.noise_map = mask.mapping.array_from_array_2d(array_2d=imaging.noise_map.in_2d)

        self.positions = None
        self.hyper_noise_map_max = None
        self.uses_cluster_inversion = False
        self.inversion_pixel_limit = 1000
        self.inversion_uses_border = True
        self.preload_pixelization_grids_of_planes = None

    def signal_to_noise_map(self):
        return self.image / self.noise_map

    def check_positions_trace_within_threshold_via_tracer(self, tracer):
        pass

    def check_inversion_pixels_are_below_limit_via_tracer(self, tracer):
        pass


class MockMaskedInterferometer(object):
    def __init__(self, interferometer, mask, grid, transformer):

        self.interferometer = interferometer
        self.mask = mask

        self.visibilities = interferometer.visibilities
        self.noise_map =  np.stack(
                (self.interferometer.noise_map, self.interferometer.noise_map), axis=-1
            )
        self.visibilities_mask = np.full(fill_value=False, shape=self.interferometer.uv_wavelengths.shape)
        self.primary_beam = interferometer.primary_beam

        self.grid = grid
        self.transformer = transformer

        self.positions = None
        self.hyper_noise_map_max = None
        self.uses_cluster_inversion = False
        self.inversion_pixel_limit = 1000
        self.inversion_uses_border = True
        self.preload_pixelization_grids_of_planes = None

    def signal_to_noise_map(self):
        return self.visibilities / self.noise_map