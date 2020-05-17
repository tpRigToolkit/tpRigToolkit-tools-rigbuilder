import os

from tpDcc.libs.python import yamlio
from tpDcc.libs.qt.widgets import project
from tpDcc.libs.nameit.core import namelib

from tpRigToolkit.tools.rigbuilder.objects import helpers


class RigBuilderProject(project.Project, object):
    def __init__(self, *args, **kwargs):
        super(RigBuilderProject, self).__init__(*args, **kwargs)

        # Force the creation of naming.yml file
        naming_file = self._create_default_naming()
        self._naming_lib = namelib.NameLib(naming_file=naming_file)
        self._naming_lib.init_naming_data()

    @property
    def naming_lib(self):

        self.get_option

        return self._naming_lib

    def get_naming_file(self):
        """
        Returns project naming file
        :return: str
        """

        return os.path.join(self.full_path, 'naming.yml')

    def get_name_rule(self):
        """
        Returns current project active name rule
        :return: Rule
        """

        if not self._naming_lib:
            return

        if not self.settings.has_setting('naming_rule'):
            return None

        rule_name = self.settings.get('naming_rule')
        if not self._naming_lib.has_rule(rule_name):
            return

        rule = self._naming_lib.get_rule(rule_name)

        return rule

    def find_rig(self, rig_name):
        """
        Tries to find a rig inside current project
        :param rig_name: str
        :return: Rig
        """

        all_rigs = helpers.RigHelpers.find_rigs(self.full_path, as_full_path=True)
        for rig_path in all_rigs:
            if os.path.basename(rig_path) == rig_name:
                rig = helpers.RigHelpers.get_rig(rig_path)
                return rig

        return None

    def _create_default_naming(self):
        naming_file = self.get_naming_file()
        if not os.path.isfile(naming_file):
            default_data = {
                'rules': [
                    {
                        '_Serializable_classname': 'Rule',
                        '_Serializable_version': '1.0',
                        'auto_fix': False,
                        'description': 'Defines the name of DCC nodes',
                        'expression': '{description}_{side}_{node_type}_{id}',
                        'iterator_format': '###',
                        'name': 'node'
                    }
                ],
                'tokens': [
                    {
                        '_Serializable_classname': 'Token',
                        '_Serializable_version': '1.0',
                        'default': 0,
                        'description': 'Description of the asset.',
                        'items':{},
                        'name': 'description',
                        'override_value': '',
                        'values': {
                            'key': [],
                            'value': []
                        }
                    },
                    {
                        '_Serializable_classname': 'Token',
                        '_Serializable_version': '1.0',
                        'default': 1,
                        'description': 'The format of the id\n\n#: Id with a unique numeric value\n\n@: Id with an alphabetic value (lowercase)\n\n@^: Id with an alphabetic value (upperase)\n\nNOTE: @ key do not need multiples keys ( @@, @@@) beause the system\nautomatically will add double alphabetic characters if we pass the ''z'' character (a...z, aa,ab, ac, ad ...)',
                        'items': {},
                        'name': 'id',
                        'override_value': '',
                        'values': {
                            'key': ['iterator'],
                            'value': ['#']
                        }
                    },
                    {
                        '_Serializable_classname': 'Token',
                        '_Serializable_version': '1.0',
                        'default': 0,
                        'description': '',
                        'items': {},
                        'name': 'node_type',
                        'override_value': '',
                        'values': {
                            'key': [],
                            'value': []
                        }
                    },
                    {
                        '_Serializable_classname': 'Token',
                        '_Serializable_version': '1.0',
                        'default': 1,
                        'description': '',
                        'name': 'side',
                        'override_value': '',
                        'values': {
                            'key': ['center', 'right', 'left'],
                            'value': ['c', 'r', 'l']
                        }
                    }
                ]
            }
            yamlio.write_to_file(default_data, naming_file)

        return naming_file
