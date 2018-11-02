import numpy as np

from autolens.imaging import image as im
from autolens.imaging import mask as msk
from autolens.fitting import fitting_data
from autolens.inversion import convolution as inversion_convolution


class LensingImage(fitting_data.FittingImage):

    def __new__(cls, image, mask, sub_grid_size=2, image_psf_shape=None, mapping_matrix_psf_shape=None, positions=None):
        return np.array(mask.map_2d_array_to_masked_1d_array(image)).view(cls)

    def __init__(self, image, mask, sub_grid_size=2, image_psf_shape=None, mapping_matrix_psf_shape=None,
                 positions=None):
        """
        The lensing datas_ is the collection of datas (image, noise-maps, PSF), a masks, grids, convolvers and other \
        utilities that are used for modeling and fitting an datas_ of a strong lens.

        Whilst the datas_ datas is initially loaded in 2D, for the lensing datas_ the masked-datas_ (and noise-maps) \
        are reduced to 1D arrays for faster calculations.

        Parameters
        ----------
        image: im.Image
            The original datas_ datas in 2D.
        mask: msk.Mask
            The 2D masks that is applied to the datas_.
        sub_grid_size : int
            The size of the sub-grid used for each lensing SubGrid. E.g. a value of 2 grids each datas_-pixel on a 2x2 \
            sub-grid.
        image_psf_shape : (int, int)
            The shape of the PSF used for convolving model image generated using analytic light profiles. A smaller \
            shape will trim the PSF relative to the input datas_ PSF, giving a faster analysis run-time.
        mapping_matrix_psf_shape : (int, int)
            The shape of the PSF used for convolving the inversion mapping matrix. A smaller \
            shape will trim the PSF relative to the input datas_ PSF, giving a faster analysis run-time.
        positions : [[]]
            Lists of datas_-pixel coordinates (arc-seconds) that mappers close to one another in the source-plane(s), used \
            to speed up the non-linear sampling.
        """
        super().__init__(image=image, mask=mask, sub_grid_size=sub_grid_size, image_psf_shape=image_psf_shape)

        if mapping_matrix_psf_shape is None:
            mapping_matrix_psf_shape = self.image.psf.shape

        self.convolver_mapping_matrix = inversion_convolution.ConvolverMappingMatrix(self.mask,
                                        self.image.psf.trim_around_centre(mapping_matrix_psf_shape))

        self.positions = positions

    def __array_finalize__(self, obj):
        super(LensingImage, self).__array_finalize__(obj)
        if isinstance(obj, LensingImage):
            self.image = obj.image
            self.mask = obj.mask
            self.blurring_mask = obj.blurring_mask
            self.convolver_image = obj.convolver_image
            self.convolver_mapping_matrix = obj.convolver_mapping_matrix
            self.sub_grid_size = obj.sub_grid_size
            self.grids = obj.grids
            self.padded_grids = obj.padded_grids
            self.borders = obj.borders
            self.positions = obj.positions


class LensingHyperImage(fitting_data.FittingHyperImage):

    def __new__(cls, image, mask, hyper_model_image, hyper_galaxy_images, hyper_minimum_values, sub_grid_size=2,
                image_psf_shape=None, mapping_matrix_psf_shape=None, positions=None):
        return np.array(mask.map_2d_array_to_masked_1d_array(image)).view(cls)

    def __init__(self, image, mask, hyper_model_image, hyper_galaxy_images, hyper_minimum_values, sub_grid_size=2,
                 image_psf_shape=None, mapping_matrix_psf_shape=None, positions=None):
        """
        The lensing datas_ is the collection of datas (image, noise-maps, PSF), a masks, grids, convolvers and other \
        utilities that are used for modeling and fitting an datas_ of a strong lens.

        Whilst the datas_ datas is initially loaded in 2D, for the lensing datas_ the masked-datas_ (and noise-maps) \
        are reduced to 1D arrays for faster calculations.

        Parameters
        ----------
        image: im.Image
            The original datas_ datas in 2D.
        mask: msk.Mask
            The 2D masks that is applied to the datas_.
        sub_grid_size : int
            The size of the sub-grid used for each lensing SubGrid. E.g. a value of 2 grids each datas_-pixel on a 2x2 \
            sub-grid.
        image_psf_shape : (int, int)
            The shape of the PSF used for convolving model image generated using analytic light profiles. A smaller \
            shape will trim the PSF relative to the input datas_ PSF, giving a faster analysis run-time.
        mapping_matrix_psf_shape : (int, int)
            The shape of the PSF used for convolving the inversion mapping matrix. A smaller \
            shape will trim the PSF relative to the input datas_ PSF, giving a faster analysis run-time.
        positions : [[]]
            Lists of datas_-pixel coordinates (arc-seconds) that mappers close to one another in the source-plane(s), used \
            to speed up the non-linear sampling.
        """
        super().__init__(image=image, mask=mask, hyper_model_image=hyper_model_image,
                         hyper_galaxy_images=hyper_galaxy_images, hyper_minimum_values=hyper_minimum_values,
                         sub_grid_size=sub_grid_size, image_psf_shape=image_psf_shape)

        if mapping_matrix_psf_shape is None:
            mapping_matrix_psf_shape = self.image.psf.shape

        self.convolver_mapping_matrix = inversion_convolution.ConvolverMappingMatrix(self.mask,
                                        self.image.psf.trim_around_centre(mapping_matrix_psf_shape))

        self.positions = positions

    def __array_finalize__(self, obj):
        super(LensingHyperImage, self).__array_finalize__(obj)
        if isinstance(obj, LensingHyperImage):
            self.image = obj.image
            self.mask = obj.mask
            self.blurring_mask = obj.blurring_mask
            self.convolver_image = obj.convolver_image
            self.convolver_mapping_matrix = obj.convolver_mapping_matrix
            self.grids = obj.grids
            self.sub_grid_size = obj.sub_grid_size
            self.padded_grids = obj.padded_grids
            self.borders = obj.borders
            self.positions = obj.positions
            self.hyper_model_image = obj.hyper_model_image
            self.hyper_galaxy_images = obj.hyper_galaxy_images
            self.hyper_minimum_values = obj.hyper_minimum_values