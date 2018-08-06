import math
from scipy.special import erfinv
import inspect
import os
from src import exc
from src.config.config import DefaultPriorConfig, WidthConfig

path = os.path.dirname(os.path.realpath(__file__))


class ModelMapper(object):
    """A collection of priors formed by passing in classes to be reconstructed
        @DynamicAttrs
    """

    def __init__(self, config=None, width_config=None, **classes):
        """
        Parameters
        ----------
        config: auto_lens.config.config.Config
            An object that wraps a configuration

        Examples
        --------
        # The ModelMapper converts a set of classes whose input attributes may be modeled using a non-linear search, to
        # parameters with priors attached.

        # A config is passed into the collection to provide default setup values for the priors:

        collection = ModelMapper(config)

        # All class instances that are to be generated by the collection are specified by passing their name and class:

        collection.add_class("sersic_1", light_profile.EllipticalSersicMass)
        collection.add_class("sersic_2", light_profile.EllipticalSersicMass)
        collection.add_class("other_instance", SomeClass)

        # A PriorModel instance is created each time we add a class to the collection. We can access those models using
        # their name:

        sersic_model_1 = collection.sersic_1

        # This allows us to replace the default priors:

        collection.sersic_1.intensity = GaussianPrior(2., 5.)

        # Or maybe we want to tie two priors together:

        collection.sersic_1.intensity = collection.sersic_2.intensity

        # This statement reduces the number of priors by one and means that the two sersic instances will always share
        # the same centre.

        # We can then create instances of every class for a unit hypercube vector with length equal to
        # len(collection.priors):

        model_instance = collection.model_instance_for_vector([.4, .2, .3, .1])

        # The attributes of the model_instance are named the same as those of the collection:

        sersic_1 = collection.sersic_1

        # But this attribute is an instance of the actual EllipticalSersicMass class

        # A ModelMapper can be concisely constructed using keyword arguments:

        collection = prior.ModelMapper(config, source_light_profile=light_profile.EllipticalSersicMass,
                                    lens_mass_profile=mass_profile.EllipticalCoredIsothermal,
                                    lens_light_profile=light_profile.EllipticalCoreSersic)
        """
        super(ModelMapper, self).__init__()

        self.config = (config if config is not None else DefaultPriorConfig("{}/../config/priors/default".format(path)))
        self.width_config = (
            width_config if width_config is not None else WidthConfig("{}/../config/priors/width".format(path)))

        for name, cls in classes.items():
            self.__setattr__(name, cls)

    @property
    def total_parameters(self):
        return len(self.priors_ordered_by_id)

    def __setattr__(self, key, value):
        if isinstance(value, list) and len(value) > 0 and isinstance(value[0], AbstractPriorModel):
            value = ListPriorModel(value)
        elif inspect.isclass(value):
            value = PriorModel(value, config=self.config)
        super(ModelMapper, self).__setattr__(key, value)

    def add_classes(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    @property
    def prior_models(self):
        """
        Returns
        -------
        prior_model_tuples: [(String, PriorModel)]
        """
        return list(filter(lambda t: isinstance(t[1], AbstractPriorModel), self.__dict__.items()))

    @property
    def list_prior_models(self):
        """
        Returns
        -------
        list_prior_model_tuples: [(String, ListPriorModel)]
        """
        return list(filter(lambda t: isinstance(t[1], ListPriorModel), self.__dict__.items()))

    @property
    def flat_prior_models(self):
        """
        Returns
        -------
        prior_model_tuples: [(String, PriorModel)]
            A list of tuples with the names of prior models and associated prior models. Names are fully qualified by
            all objects in which they are embedded.
        """
        return [("{}".format(prior_model_name), flat_prior_model) for
                prior_model_name, prior_model in
                self.prior_models for
                flat_prior_model_name, flat_prior_model in
                prior_model.flat_prior_models]

    @property
    def prior_set(self):
        """
        Returns
        -------
        prior_set: set()
            The set of all priors associated with this collection
        """
        return {prior[1]: prior for name, prior_model in self.prior_models for prior in
                prior_model.priors}.values()

    @property
    def prior_class_dict(self):
        return {prior: cls for prior_model in self.prior_models for prior, cls in
                prior_model[1].prior_class_dict.items()}

    @property
    def priors_ordered_by_id(self):
        """
        Returns
        -------
        priors: [Prior]
            An ordered list of unique priors associated with this collection
        """
        return sorted(list(self.prior_set), key=lambda prior: prior[1].id)

    @property
    def class_priors_dict(self):
        """
        Returns
        -------
        class_priors_dict: {String: [Prior]}
            A dictionary mapping the names of reconstructable class instances to lists of associated priors
        """
        return {name: list(prior_model.priors) for name, prior_model in self.prior_models}

    def physical_vector_from_hypercube_vector(self, hypercube_vector):
        """
        Parameters
        ----------
        hypercube_vector: [float]
            A unit hypercube vector

        Returns
        -------
        values: [float]
            A vector with values output by priors
        """
        return list(map(lambda prior, unit: prior[1].value_for(unit), self.priors_ordered_by_id, hypercube_vector))

    def physical_values_ordered_by_class(self, hypercube_vector):
        model_instance = self.instance_from_unit_vector(hypercube_vector)
        result = []
        for instance_key in sorted(model_instance.__dict__.keys()):
            instance = model_instance.__dict__[instance_key]
            for attribute_key in sorted(instance.__dict__.keys()):

                value = instance.__dict__[attribute_key]

                if isinstance(value, tuple):
                    result.extend(list(value))
                else:
                    result.append(value)
        return result

    @property
    def physical_vector_from_prior_medians(self):
        return self.physical_vector_from_hypercube_vector([0.5] * len(self.prior_set))

    def instance_from_prior_medians(self):
        """
        Creates a list of physical values from the median values of the priors.

        Returns
        -------
        physical_values : [float]
            A list of physical values

        """
        return self.instance_from_unit_vector(unit_vector=[0.5] * len(self.prior_set))

    def instance_from_unit_vector(self, unit_vector):
        """
        Creates a ModelInstance, which has an attribute and class instance corresponding to every PriorModel attributed
        to this instance.

        This method takes as input a unit vector of parameter values, converting each to physical values via their \
        priors.

        Parameters
        ----------
        unit_vector: [float]
            A vector of physical parameter values.

        Returns
        -------
        model_instance : ModelInstance
            An object containing reconstructed model_mapper instances

        """
        arguments = dict(
            map(lambda prior, unit: (prior[1], prior[1].value_for(unit)), self.priors_ordered_by_id, unit_vector))

        return self.instance_from_arguments(arguments)

    def instance_from_physical_vector(self, physical_vector):
        """
        Creates a ModelInstance, which has an attribute and class instance corresponding to every PriorModel attributed
        to this instance.

        This method takes as input a physical vector of parameter values, thus omitting the use of priors.

        Parameters
        ----------
        physical_vector: [float]
            A unit hypercube vector

        Returns
        -------
        model_instance : ModelInstance
            An object containing reconstructed model_mapper instances

        """
        arguments = dict(
            map(lambda prior, physical_unit: (prior[1], physical_unit), self.priors_ordered_by_id, physical_vector))

        return self.instance_from_arguments(arguments)

    def mapper_from_prior_arguments(self, arguments):
        """
        Creates a new model mapper from a dictionary mapping existing priors to new priors.

        Parameters
        ----------
        arguments: {Prior: Prior}
            A dictionary mapping priors to priors

        Returns
        -------
        model_mapper: ModelMapper
            A new model mapper with updated priors.
        """
        mapper = ModelMapper(config=self.config, width_config=self.width_config)

        for prior_model in self.prior_models:
            setattr(mapper, prior_model[0], prior_model[1].gaussian_prior_model_for_arguments(arguments))

        return mapper

    def mapper_from_gaussian_tuples(self, tuples):
        """
        Creates a new model mapper from a list of tuples describing the mean and width values of gaussian priors. The
        new gaussian priors must be provided in the same order as the priors associated with model.

        Parameters
        ----------
        tuples: [(float, float)]
            A list of tuples containing the mean and sigma of the gaussian priors.

        Returns
        -------
        mapper: ModelMapper
            A new model mapper with all priors replaced by gaussian priors.
        """
        new_priors = map(lambda t: GaussianPrior(t[0], t[1]), tuples)
        arguments = dict(map(lambda prior, new_prior: (prior[1], new_prior), self.priors_ordered_by_id, new_priors))

        return self.mapper_from_prior_arguments(arguments)

    def mapper_from_gaussian_means(self, means):
        """
        Creates a new model mapper from a list of floats describing the mean values of gaussian priors. The widths of
        the new priors are taken from the width_config. The new gaussian priors must be provided in the same order as
        the priors associated with model.

        Parameters
        ----------
        means: [float]
            A list containing the means of the gaussian priors.

        Returns
        -------
        mapper: ModelMapper
            A new model mapper with all priors replaced by gaussian priors.
        """
        priors = self.priors_ordered_by_id
        prior_class_dict = self.prior_class_dict
        arguments = {}

        for i, prior in enumerate(priors):
            cls = prior_class_dict[prior[1]]
            width = self.width_config.get_for_nearest_ancestor(cls, prior[0])
            arguments[prior[1]] = GaussianPrior(means[i], width)

        return self.mapper_from_prior_arguments(arguments)

    def instance_from_arguments(self, arguments):
        """
        Creates a ModelInstance, which has an attribute and class instance corresponding to every PriorModel attributed
        to this instance.

        Parameters
        ----------
        arguments : dict
            The dictionary representation of prior and parameter values. This is created in the model_instance_from_* \
            routines.

        Returns
        -------
        model_instance : ModelInstance
            An object containing reconstructed model_mapper instances

        """

        model_instance = ModelInstance()

        for prior_model in self.prior_models:
            setattr(model_instance, prior_model[0], prior_model[1].instance_for_arguments(arguments))

        return model_instance

    def generate_model_info(self):
        """
        Use the priors that make up the model_mapper to information on each parameter of the overall model.

        This information is extracted from each priors *model_info* property.
        """

        model_info = ''

        for prior_name, prior_model in self.flat_prior_models:

            model_info += prior_model.cls.__name__ + '\n' + '\n'

            for i, prior in enumerate(prior_model.priors):
                param_name = str(self.class_priors_dict[prior_name][i][0])
                model_info += param_name + ': ' + (prior[1].model_info + '\n')

            model_info += '\n'

        return model_info

    def output_model_info(self, filename):
        """Output a model information file, which lists the information of the model mapper (e.g. parameters, priors,
         etc.) """
        model_info = self.generate_model_info()
        if not os.path.isfile(filename):
            with open(filename, 'w') as file:
                file.write(model_info)
            file.close()

    def check_model_info(self, filename):
        """Check whether the priors in this instance of the model_mapper are identical to those output into a model \
        info file on the hard-disk (e.g. from a previous non-linear search)."""

        model_info = self.generate_model_info()

        model_info_check = open(filename, 'r')

        if str(model_info_check.read()) != model_info:
            raise exc.PriorException(
                'The model_mapper input to MultiNest has a different prior for a parameter than the model_mapper '
                'existing in the nlo. filename = {}'.format(filename))

        model_info_check.close()


class ModelInstance(object):
    """
    An object to hold model instances produced by providing arguments to a model mapper.

    @DynamicAttrs
    """

    def instances_of(self, cls):
        return [instance for source in
                [list(self.__dict__.values())] + [ls for ls in self.__dict__.values() if isinstance(ls, list)] for
                instance in
                source if isinstance(instance, cls)]


class Constant(object):
    def __init__(self, value):
        """
        Represents a constant value. No prior is added to the model mapper for constants reducing the dimensionality
        of the nonlinear search.

        Parameters
        ----------
        value: Union(float, tuple)
            The value this constant should take.
        """
        self.value = value

    def __eq__(self, other):
        return self.value == other

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other

    def __ne__(self, other):
        return self.value != other

    def __str__(self):
        return "Constant {}".format(self.value)


prior_number = 0


class Prior(object):
    """An object used to map a unit value to an attribute value for a specific class attribute"""

    def __init__(self):
        global prior_number
        self.id = prior_number
        prior_number += 1

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "<Prior id={}>".format(self.id)


class UniformPrior(Prior):
    """A prior with a uniform distribution between a lower and upper limit"""

    def __init__(self, lower_limit=0., upper_limit=1.):
        """

        Parameters
        ----------
        lower_limit: Float
            The lowest value this prior can return
        upper_limit: Float
            The highest value this prior can return
        """
        super(UniformPrior, self).__init__()
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    def value_for(self, unit):
        """

        Parameters
        ----------
        unit: Float
            A unit hypercube value between 0 and 1
        Returns
        -------
        value: Float
            A value for the attribute between the upper and lower limits
        """
        return self.lower_limit + unit * (self.upper_limit - self.lower_limit)

    @property
    def model_info(self):
        """The line of text describing this prior for the model_mapper.info file"""
        return 'UniformPrior, lower_limit = ' + str(self.lower_limit) + ', upper_limit = ' + str(self.upper_limit)


class GaussianPrior(Prior):
    """A prior with a gaussian distribution"""

    def __init__(self, mean, sigma):
        super(GaussianPrior, self).__init__()
        self.mean = mean
        self.sigma = sigma

    def value_for(self, unit):
        """

        Parameters
        ----------
        unit: Float
            A unit hypercube value between 0 and 1
        Returns
        -------
        value: Float
            A value for the attribute biased to the gaussian distribution
        """
        return self.mean + (self.sigma * math.sqrt(2) * erfinv((unit * 2.0) - 1.0))

    @property
    def model_info(self):
        """The line of text describing this prior for the model_mapper.info file"""
        return 'GaussianPrior, mean = ' + str(self.mean) + ', sigma = ' + str(self.sigma)


class TuplePrior(object):
    """
    A prior comprising one or more priors in a tuple
    """

    @property
    def priors(self):
        """
        Returns
        -------
        priors: [(String, Prior)]
            A list of priors contained in this tuple
        """
        return list(filter(lambda t: isinstance(t[1], Prior), self.__dict__.items()))

    def value_for_arguments(self, arguments):
        """
        Parameters
        ----------
        arguments: {Prior: float}
            A dictionary of arguments

        Returns
        -------
        tuple: (float,...)
            A tuple of float values
        """
        return tuple([arguments[prior[1]] for prior in self.priors])

    def gaussian_tuple_prior_for_arguments(self, arguments):
        """
        Parameters
        ----------
        arguments: {Prior: float}
            A dictionary of arguments

        Returns
        -------
        tuple_prior: TuplePrior
            A new tuple prior with gaussian priors
        """
        tuple_prior = TuplePrior()
        for prior in self.priors:
            setattr(tuple_prior, prior[0], arguments[prior[1]])
        return tuple_prior


class AbstractPriorModel:
    """
    Abstract model that maps a set of priors to a particular class. Must be overridden by any prior model so that the
    model mapper recognises its prior model attributes.
    """

    @property
    def flat_prior_models(self):
        """
        Returns
        -------
        prior_models: [(str, AbstractPriorModel)]
            A list of prior models associated with this instance
        """
        raise NotImplementedError("PriorModels must implement the flat_prior_models property")


class PriorModel(AbstractPriorModel):
    """Object comprising class and associated priors
        @DynamicAttrs
    """

    @property
    def flat_prior_models(self):
        return [("", self)]

    def __init__(self, cls, config=None):
        """
        Parameters
        ----------
        cls: class
            The class associated with this instance
        """

        self.cls = cls
        self.config = (config if config is not None else DefaultPriorConfig("{}/../config/priors/default".format(path)))

        arg_spec = inspect.getfullargspec(cls.__init__)

        try:
            defaults = dict(zip(arg_spec.args[-len(arg_spec.defaults):], arg_spec.defaults))
        except TypeError:
            defaults = {}

        args = arg_spec.args[1:]

        if 'settings' in defaults:
            del defaults['settings']
        if 'settings' in args:
            args.remove('settings')

        for arg in args:
            if arg in defaults and isinstance(defaults[arg], tuple):
                tuple_prior = TuplePrior()
                for i in range(len(defaults[arg])):
                    attribute_name = "{}_{}".format(arg, i)
                    setattr(tuple_prior, attribute_name, self.make_prior(attribute_name, cls))
                setattr(self, arg, tuple_prior)
            else:
                setattr(self, arg, self.make_prior(arg, cls))

    def make_prior(self, attribute_name, cls):
        config_arr = self.config.get_for_nearest_ancestor(cls, attribute_name)
        if config_arr[0] == "u":
            return UniformPrior(config_arr[1], config_arr[2])
        elif config_arr[0] == "g":
            return GaussianPrior(config_arr[1], config_arr[2])
        elif config_arr[0] == "c":
            return Constant(config_arr[1])

    @property
    def tuple_priors(self):
        """
        Returns
        -------
        tuple_prior_tuples: [(String, TuplePrior)]
        """
        return list(filter(lambda t: isinstance(t[1], TuplePrior), self.__dict__.items()))

    @property
    def direct_priors(self):
        """
        Returns
        -------
        direct_priors: [(String, Prior)]
        """
        return list(filter(lambda t: isinstance(t[1], Prior), self.__dict__.items()))

    @property
    def priors(self):
        """
        Returns
        -------
        priors: [(String, Union(Prior, TuplePrior))]
        """
        return [prior for tuple_prior in self.tuple_priors for prior in
                tuple_prior[1].priors] + self.direct_priors

    @property
    def constants(self):
        """
        Returns
        -------
        constants: [(String, Constant)]
            A list of constants
        """
        return list(filter(lambda t: isinstance(t[1], Constant), self.__dict__.items()))

    @property
    def prior_class_dict(self):
        return {prior[1]: self.cls for prior in self.priors}

    def instance_for_arguments(self, arguments):
        """
        Create an instance of the associated class for a set of arguments

        Parameters
        ----------
        arguments: {Prior: value}
            Dictionary mapping priors to attribute name and value pairs

        Returns
        -------
            An instance of the class
        """
        model_arguments = {t[0]: arguments[t[1]] for t in self.direct_priors}
        for tuple_prior in self.tuple_priors:
            model_arguments[tuple_prior[0]] = tuple_prior[1].value_for_arguments(arguments)

        constant_arguments = {t[0]: t[1].value for t in self.constants}

        return self.cls(**{**model_arguments, **constant_arguments})

    def gaussian_prior_model_for_arguments(self, arguments):
        """
        Create a new instance of model mapper with a set of Gaussian priors based on tuples provided by a previous
        nonlinear search.

        Parameters
        ----------
        arguments: [(float, float)]
            Tuples providing the mean and sigma of gaussians

        Returns
        -------
        new_model: ModelMapper
            A new model mapper populated with Gaussian priors
        """
        new_model = PriorModel(self.cls, self.config)

        model_arguments = {t[0]: arguments[t[1]] for t in self.direct_priors}

        for tuple_prior in self.tuple_priors:
            setattr(new_model, tuple_prior[0], tuple_prior[1].gaussian_tuple_prior_for_arguments(arguments))
        for prior in self.direct_priors:
            setattr(new_model, prior[0], model_arguments[prior[0]])
        for constant in self.constants:
            setattr(new_model, constant[0], constant[1])

        return new_model


class ListPriorModel(list, AbstractPriorModel):
    @property
    def flat_prior_models(self):
        return [flat_prior_model for prior_model in self for flat_prior_model in prior_model.flat_prior_models]

    def __init__(self, prior_models):
        """
        A prior model used to represent a list of prior models for convenience.

        Parameters
        ----------
        prior_models: [PriorModel]
            A list of prior models
        """
        super().__init__(prior_models)

    def instance_for_arguments(self, arguments):
        """
        Parameters
        ----------
        arguments: {Prior: float}
            A dictionary of arguments

        Returns
        -------
        model_instances: [object]
            A list of instances constructed from the list of prior models.
        """
        return [prior_model.instance_for_arguments(arguments) for prior_model in self]

    def gaussian_prior_model_for_arguments(self, arguments):
        """
        Parameters
        ----------
        arguments: {Prior: float}
            A dictionary of arguments

        Returns
        -------
        prior_models: [PriorModel]
            A new list of prior models with gaussian priors
        """
        return ListPriorModel(
            [prior_model.gaussian_prior_model_for_arguments(arguments) for prior_model in self])

    @property
    def priors(self):
        """
        Returns
        -------
        priors: [(String, Union(Prior, TuplePrior))]
        """
        return set([prior for prior_model in self for prior in prior_model.priors])

    @property
    def prior_class_dict(self):
        return {prior: cls for prior_model in self for prior, cls in prior_model.prior_class_dict.items()}
