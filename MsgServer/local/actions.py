import yaml
from yamlordereddictloader import Loader

class Action:
    actions = yaml.load(open('actions.yml', 'r'), Loader=Loader)

    @classmethod
    def get(cls, action, params):
        """
        Return a formatted string that will be sent to the applicable channel.

        :param action: Action params are associated with
        :type action: str
        :param params: Parameters to use
        :type params: dict
        :return: A formatted string
        :rtype: str
        """
        cls.actions.get(action)