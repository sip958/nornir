import os


import yaml


CONF = {
    'num_workers': {
        'description': 'Number of Brigade worker processes that are run at the same time, '
                       'configuration can be overridden on individual tasks by using the '
                       '`num_workers` argument to (:obj:`brigade.core.Brigade.run`)',
        'type': 'int',
        'default': 20,
    },
    'raise_on_error': {
        'description': "If set to ``True``, (:obj:`brigade.core.Brigade.run`) method of will raise "
                       "an exception if at least a host failed.",
        'type': 'bool',
        'default': True,
    },
    'ssh_config_file': {
        'description': 'User ssh_config_file',
        'type': 'str',
        'default': os.path.join(os.path.expanduser("~"), ".ssh", "config"),
        'default_doc': '~/.ssh/config'
    },
}

types = {
    'int': int,
    'str': str,
}


class Config:
    """
    This object handles the configuration of Brigade.

    Arguments:
        config_file(``str``): Yaml configuration file.
    """

    def __init__(self, config_file=None, **kwargs):
        if config_file:
            with open(config_file, 'r') as f:
                data = yaml.load(f.read()) or {}
        else:
            data = {}

        for parameter, param_conf in CONF.items():
            self._assign_property(parameter, param_conf, data)

        for k, v in data.items():
            if k not in CONF:
                setattr(self, k, v)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def string_to_bool(self, v):
        if v.lower() in ["false", "no", "n", "off", "0"]:
            return False
        else:
            return True

    def _assign_property(self, parameter, param_conf, data):
        env = param_conf.get('env') or 'BRIGADE_' + parameter.upper()
        v = os.environ.get(env)
        if v is None:
            v = data.get(parameter, param_conf["default"])
        else:
            if param_conf['type'] == 'bool':
                v = self.string_to_bool(v)
            else:
                v = types[param_conf['type']](v)
        setattr(self, parameter, v)

    def get(self, parameter, env=None, default=None, parameter_type="str", root=""):
        """
        Retrieve a custom parameter from the configuration.

        Arguments:
            parameter(str): Name of the parameter to retrieve
            env(str): Environment variable name to retrieve the object from
            default: default value in case no parameter is found
            parameter_type(str): if a value is found cast the variable to this type
            root(str): parent key in the configuration file where to look for the parameter
        """
        value = os.environ.get(env) if env else None
        if value is None:
            if root:
                d = getattr(self, root, {})
                value = d.get(parameter, default)
            else:
                value = getattr(self, parameter, default)
        if parameter_type in [bool, "bool"]:
            if not isinstance(value, bool):
                value = self.string_to_bool(value)
        else:
            value = types[str(parameter_type)](value)
        return value
