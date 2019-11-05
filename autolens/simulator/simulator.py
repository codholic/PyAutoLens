import autofit as af
from autoarray.structures import grids
from autoarray.simulator import simulator
from autoarray.plotters import imaging_plotters
from autolens.lens import ray_tracing


class ImagingSimulator(simulator.ImagingSimulator):
    def __init__(
        self,
        shape_2d,
        pixel_scales,
        sub_size,
        psf,
        exposure_time,
        background_sky_level,
        add_noise=True,
        noise_if_add_noise_false=0.1,
        noise_seed=-1,
        origin=(0.0, 0.0),
    ):
        """A class representing a Imaging observation, using the shape of the image, the pixel scale,
        psf, exposure time, etc.

        Parameters
        ----------
        shape_2d : (int, int)
            The shape of the observation. Note that we do not simulator a full Imaging frame (e.g. 2000 x 2000 pixels for \
            Hubble imaging), but instead just a cut-out around the strong lens.
        pixel_scales : float
            The size of each pixel in arc seconds.
        psf : PSF
            An arrays describing the PSF kernel of the image.
        exposure_time : float
            The exposure time of an observation using this data_type.
        background_sky_level : float
            The level of the background sky of an observationg using this data_type.
        """

        super(ImagingSimulator, self).__init__(
            shape_2d=shape_2d,
            pixel_scales=pixel_scales,
            sub_size=sub_size,
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
            add_noise=add_noise,
            noise_if_add_noise_false=noise_if_add_noise_false,
            noise_seed=noise_seed,
            origin=origin,
        )

    def from_galaxies(self, galaxies, plot_imaging=False):
        """Simulate Imaging data_type for this data_type, as follows:

        1)  Setup the image-plane grid of the Imaging arrays, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image of \
           the simulated Imaging data_type.

        3) Simulate the Imaging data_type, using a special image which ensures edge-effects don't
           degrade simulator of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_imaging bool is True.

        5) Output the dataset to .fits format if a dataset_path and data_name are specified. Otherwise, return the simulated \
           imaging data_type instance."""

        tracer = ray_tracing.Tracer.from_galaxies(galaxies=galaxies)

        imaging = self.from_tracer(tracer=tracer)

        if plot_imaging:
            imaging_plotters.subplot(imaging=imaging)

        return imaging

    def from_galaxies_and_write_to_fits(
        self, galaxies, dataset_path, data_name, plot_imaging=False
    ):
        """Simulate Imaging data_type for this data_type, as follows:

        1)  Setup the image-plane grid of the Imaging arrays, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image of \
           the simulated Imaging data_type.

        3) Simulate the Imaging data_type, using a special image which ensures edge-effects don't
           degrade simulator of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_imaging bool is True.

        5) Output the dataset to .fits format if a dataset_path and data_name are specified. Otherwise, return the simulated \
           imaging data_type instance."""

        imaging = self.from_galaxies(
            galaxies=galaxies,
            plot_imaging=plot_imaging,
        )

        data_output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
            path=dataset_path, folder_names=[data_name]
        )

        imaging.output_to_fits(
            image_path=data_output_path + "image.fits",
            psf_path=data_output_path + "psf.fits",
            noise_map_path=data_output_path + "noise_map.fits",
            exposure_time_map_path=data_output_path + "exposure_time_map.fits",
            background_noise_map_path=data_output_path + "background_noise_map.fits",
            poisson_noise_map_path=data_output_path + "poisson_noise_map.fits",
            background_sky_map_path=data_output_path + "background_sky_map.fits",
            overwrite=True,
        )

    def from_deflections_and_galaxies(self, deflections, galaxies, name=None):

        grid = grids.Grid.uniform(
            shape_2d=deflections.shape_2d,
            pixel_scales=deflections.pixel_scales,
            sub_size=1,
        )

        deflected_grid = grid - deflections.in_1d_binned

        image_2d = sum(
            map(lambda g: g.profile_image_from_grid(grid=deflected_grid), galaxies)
        )

        return self.from_image(image=image_2d, name=name)

    def from_tracer(self, tracer, name=None):
        """
        Create a realistic simulated image by applying effects to a plain simulated image.

        Parameters
        ----------
        name
        image : ndarray
            The image before simulating (e.g. the lens and source galaxies before optics blurring and Imaging read-out).
        pixel_scales: float
            The scale of each pixel in arc seconds
        exposure_time_map : ndarray
            An arrays representing the effective exposure time of each pixel.
        psf: PSF
            An arrays describing the PSF the simulated image is blurred with.
        background_sky_map : ndarray
            The value of background sky in every image pixel (electrons per second).
        add_noise: Bool
            If True poisson noise_maps is simulated and added to the image, based on the total counts in each image
            pixel
        noise_seed: int
            A seed for random noise_maps generation
        """

        grid = grids.Grid.uniform(
            shape_2d=self.shape_2d,
            pixel_scales=self.pixel_scales,
            sub_size=self.sub_size,
        )

        image = tracer.padded_profile_image_from_grid_and_psf_shape(
            grid=grid, psf_shape_2d=self.psf.shape_2d
        )

        return self.from_image(image=image.in_1d_binned, name=name)


class InterferometerSimulator(simulator.ImagingSimulator):
    def __init__(
        self,
        shape_2d,
        pixel_scales,
        sub_size,
        psf,
        exposure_time,
        background_sky_level,
        add_noise=True,
        noise_if_add_noise_false=0.1,
        noise_seed=-1,
        origin=(0.0, 0.0),
    ):
        """A class representing a Imaging observation, using the shape of the image, the pixel scale,
        psf, exposure time, etc.

        Parameters
        ----------
        shape_2d : (int, int)
            The shape of the observation. Note that we do not simulator a full Imaging frame (e.g. 2000 x 2000 pixels for \
            Hubble imaging), but instead just a cut-out around the strong lens.
        pixel_scales : float
            The size of each pixel in arc seconds.
        psf : PSF
            An arrays describing the PSF kernel of the image.
        exposure_time : float
            The exposure time of an observation using this data_type.
        background_sky_level : float
            The level of the background sky of an observationg using this data_type.
        """

        super(ImagingSimulator, self).__init__(
            shape_2d=shape_2d,
            pixel_scales=pixel_scales,
            sub_size=sub_size,
            psf=psf,
            exposure_time=exposure_time,
            background_sky_level=background_sky_level,
            add_noise=add_noise,
            noise_if_add_noise_false=noise_if_add_noise_false,
            noise_seed=noise_seed,
            origin=origin,
        )

    def from_galaxies(self, galaxies, plot_imaging=False):
        """Simulate Imaging data_type for this data_type, as follows:

        1)  Setup the image-plane grid of the Imaging arrays, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image of \
           the simulated Imaging data_type.

        3) Simulate the Imaging data_type, using a special image which ensures edge-effects don't
           degrade simulator of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_imaging bool is True.

        5) Output the dataset to .fits format if a dataset_path and data_name are specified. Otherwise, return the simulated \
           imaging data_type instance."""

        tracer = ray_tracing.Tracer.from_galaxies(galaxies=galaxies)

        imaging = self.from_tracer(tracer=tracer)

        if plot_imaging:
            imaging_plotters.subplot(imaging=imaging)

        return imaging

    def from_galaxies_and_write_to_fits(
        self, galaxies, dataset_path, data_name, plot_imaging=False
    ):
        """Simulate Imaging data_type for this data_type, as follows:

        1)  Setup the image-plane grid of the Imaging arrays, which defines the coordinates used for the ray-tracing.

        2) Use this grid and the lens and source galaxies to setup a tracer, which generates the image of \
           the simulated Imaging data_type.

        3) Simulate the Imaging data_type, using a special image which ensures edge-effects don't
           degrade simulator of the telescope optics (e.g. the PSF convolution).

        4) Plot the image using Matplotlib, if the plot_imaging bool is True.

        5) Output the dataset to .fits format if a dataset_path and data_name are specified. Otherwise, return the simulated \
           imaging data_type instance."""

        imaging = self.from_galaxies(
            galaxies=galaxies,
            plot_imaging=plot_imaging,
        )

        data_output_path = af.path_util.make_and_return_path_from_path_and_folder_names(
            path=dataset_path, folder_names=[data_name]
        )

        imaging.output_to_fits(
            image_path=data_output_path + "image.fits",
            psf_path=data_output_path + "psf.fits",
            noise_map_path=data_output_path + "noise_map.fits",
            exposure_time_map_path=data_output_path + "exposure_time_map.fits",
            background_noise_map_path=data_output_path + "background_noise_map.fits",
            poisson_noise_map_path=data_output_path + "poisson_noise_map.fits",
            background_sky_map_path=data_output_path + "background_sky_map.fits",
            overwrite=True,
        )

    def from_deflections_and_galaxies(self, deflections, galaxies, name=None):

        grid = grids.Grid.uniform(
            shape_2d=deflections.shape_2d,
            pixel_scales=deflections.pixel_scales,
            sub_size=1,
        )

        deflected_grid = grid - deflections.in_1d_binned

        image_2d = sum(
            map(lambda g: g.profile_image_from_grid(grid=deflected_grid), galaxies)
        )

        return self.from_image(image=image_2d, name=name)

    def from_tracer(self, tracer, name=None):
        """
        Create a realistic simulated image by applying effects to a plain simulated image.

        Parameters
        ----------
        name
        image : ndarray
            The image before simulating (e.g. the lens and source galaxies before optics blurring and Imaging read-out).
        pixel_scales: float
            The scale of each pixel in arc seconds
        exposure_time_map : ndarray
            An arrays representing the effective exposure time of each pixel.
        psf: PSF
            An arrays describing the PSF the simulated image is blurred with.
        background_sky_map : ndarray
            The value of background sky in every image pixel (electrons per second).
        add_noise: Bool
            If True poisson noise_maps is simulated and added to the image, based on the total counts in each image
            pixel
        noise_seed: int
            A seed for random noise_maps generation
        """

        grid = grids.Grid.uniform(
            shape_2d=self.shape_2d,
            pixel_scales=self.pixel_scales,
            sub_size=self.sub_size,
        )

        image = tracer.padded_profile_image_from_grid_and_psf_shape(
            grid=grid, psf_shape_2d=self.psf.shape_2d
        )

        return self.from_image(image=image.in_1d_binned, name=name)
