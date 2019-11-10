import autofit as af
from autoarray.exc import InversionException
from autoastro.galaxy import galaxy as g
from autofit.exc import FitException
from autolens.fit import fit
from autolens.pipeline import visualizer
from autolens.pipeline.phase.dataset import analysis as analysis_data


class Analysis(analysis_data.Analysis):
    def __init__(self, masked_interferometer, cosmology, image_path=None, results=None):

        super(Analysis, self).__init__(cosmology=cosmology)

        self.visualizer = visualizer.PhaseInterferometerVisualizer(
            masked_interferometer, image_path
        )

        self.masked_interferometer = masked_interferometer

        if results is not None and results.last is not None:
            last_results = results.last

            # self.visualizer.plot_hyper_visibilities(last_results)

            self.hyper_galaxy_visibilities_path_dict = (
                last_results.hyper_galaxy_visibilities_path_dict
            )

            self.hyper_model_visibilities = last_results.hyper_model_visibilities

            # self.visualizer.plot_hyper_visibilities(last_results=last_results)

    def fit(self, instance):
        """
        Determine the fit of a lens galaxy and source galaxy to the masked_interferometer in this lens.

        Parameters
        ----------
        instance
            A model instance with attributes

        Returns
        -------
        fit : Fit
            A fractional value indicating how well this model fit and the model masked_interferometer itself
        """

        self.associate_visibilities(instance=instance)
        tracer = self.tracer_for_instance(instance=instance)

        self.masked_interferometer.check_positions_trace_within_threshold_via_tracer(
            tracer=tracer
        )
        self.masked_interferometer.check_inversion_pixels_are_below_limit_via_tracer(
            tracer=tracer
        )

        hyper_background_noise = self.hyper_background_noise_for_instance(
            instance=instance
        )

        try:
            fit = self.masked_interferometer_fit_for_tracer(
                tracer=tracer, hyper_background_noise=hyper_background_noise
            )

            return fit.figure_of_merit
        except InversionException as e:
            raise FitException from e

    def associate_visibilities(self, instance: af.ModelInstance) -> af.ModelInstance:
        """
        Takes visibilities from the last result, if there is one, and associates them with galaxies in this phase
        where full-path galaxy names match.

        If the galaxy collection has a different name then an association is not made.

        e.g.
        galaxies.lens will match with:
            galaxies.lens
        but not with:
            galaxies.lens
            galaxies.source

        Parameters
        ----------
        instance
            A model instance with 0 or more galaxies in its tree

        Returns
        -------
        instance
           The input instance with visibilities associated with galaxies where possible.
        """
        if hasattr(self, "hyper_galaxy_visibilities_path_dict"):
            for galaxy_path, galaxy in instance.path_instance_tuples_for_class(
                g.Galaxy
            ):
                if galaxy_path in self.hyper_galaxy_visibilities_path_dict:
                    galaxy.hyper_model_visibilities = self.hyper_model_visibilities
                    galaxy.hyper_galaxy_visibilities = self.hyper_galaxy_visibilities_path_dict[
                        galaxy_path
                    ]

        return instance

    def masked_interferometer_fit_for_tracer(self, tracer, hyper_background_noise):

        return fit.InterferometerFit(
            masked_interferometer=self.masked_interferometer,
            tracer=tracer,
            hyper_background_noise=hyper_background_noise,
        )

    def visualize(self, instance, during_analysis):
        instance = self.associate_visibilities(instance=instance)
        tracer = self.tracer_for_instance(instance=instance)
        hyper_background_noise = self.hyper_background_noise_for_instance(
            instance=instance
        )

        fit = self.masked_interferometer_fit_for_tracer(
            tracer=tracer, hyper_background_noise=hyper_background_noise
        )
        self.visualizer.plot_ray_tracing(fit.tracer, during_analysis)
        self.visualizer.plot_fit(fit, during_analysis)
