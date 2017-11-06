"""
Centralize the events
"""

from flask import current_app

from app.events.events_handler_template import EVENT_HANDLERS_TEMPLATE


class Tree:
    """
    Tree can be used to represent a tree of object ::

        >>> t = Tree({
        ...     'node_1': ('leaf_1_1', 'leaf_1_2'),
        ...     'node_2': ('leaf_2_1', {'node_2_2': ('leaf_2_2_1', 'leaf_2_2_2')}),
        ... })
        ...
        >>> t.node_1.leaf_1_1
        'node_1.leaf_1_1'
        >>> t.node_1.node_2_2.leaf_2_2_1
        'node_1.node_2_2.leaf_2_2_1'

    Each node in the tree is a Tree object, each leaf is build
    using :method:`build_leaf`

    Tree can be used as an iterable to walk the leafs recursively

        >>> len(t)
        5
        >>> [x for x in t]
        ['node_1.leaf_1_1', 'node_1.leaf_1_2', 'node_2.leaf_2_1',
         'node_2.node_2_2.leaf_2_2_1', 'node_2.node_2_2.leaf_2_2_2']
    """

    def __init__(self, nodes, basename=''):
        self.nodes = []
        if basename:
            make = lambda *args: basename + '.' + '.'.join(args)  # noqa: E731
        else:
            make = lambda *args: '.'.join(args)  # noqa: E731
        if isinstance(nodes, dict):
            for key, value in nodes.items():
                self._set_leaf(key, self.__class__(value, make(key)))
        elif isinstance(nodes, (tuple, list, set)):
            for node in nodes:
                if isinstance(node, str):
                    self._set_leaf(node, self.build_leaf(make(node)))
                elif isinstance(node, dict):
                    for key, value in node.items():
                        self._set_leaf(key, self.__class__(value, make(key)))
                else:
                    raise ValueError('Bad node type' % node)
        elif isinstance(nodes, str):
            self._set_leaf(nodes, self.build_leaf(make(nodes)))
        else:
            raise ValueError('Bad node type' % nodes)

    def build_leaf(self, route):
        return route

    def _set_leaf(self, key, value):
        setattr(self, key, value)
        self.nodes.append(value)

    def __iter__(self):
        for node in self.nodes:
            if isinstance(node, Tree):
                for sub_node in node:
                    yield sub_node
            else:
                yield node

    def __len__(self):
        return len([e for e in self])

    def __getitem__(self, i):
        return [e for e in self][i]

    def __str__(self):
        return str([e for e in self])


class Event:

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Event %s>' % self.name

    def __eq__(self, other):
        if isinstance(other, Event):
            return self.name == other.name
        else:
            return self.name == other

    def send(self, origin=None, **kwargs):
        # broker_rabbit = current_app.extensions['broker_rabbit']
        # return broker_rabbit.send(self.name, origin=origin, context=kwargs)
        pass


class EventTree(Tree):

    def build_leaf(self, route):
        return Event(route)


EVENTS = EventTree({
    'utilisateur': ('cree', 'modifie'),
    'site': ('cree', 'modifie', 'ferme', {'creneaux': ('cree', 'supprime')}),
    'recueil_da': ('modifie', 'pa_realise', 'demandeurs_identifies',
                   'exploite', 'exploite_by_step', 'annule', {'prefecture_rattachee': 'modifie'}),
    'droit': ('cree', 'retire', 'refus', 'modifie', {'prefecture_rattachee': 'modifie'},
              {'support': ('cree', 'modifie', 'annule')}),
    'demande_asile': ('cree', 'modifie', 'oriente', 'procedure_requalifiee',
                      'en_cours_procedure_dublin', 'en_attente_ofpra',
                      'attestation_edite', 'procedure_finie', 'introduit_ofpra', 'dublin_modifie',
                      'decision_definitive', 'decision_attestation',
                      'recevabilite_ofpra',
                      {'prefecture_rattachee': 'modifie'}),
    'usager': ('cree', 'modifie', {'etat_civil': ('modifie', 'valide')},
               {'localisation': 'modifie'}, {'prefecture_rattachee': 'modifie'}),

    'telemOfpra': ('cree'),
    'declaration': ({'vlsts': 'cree'}),
})


def init_events(app):

    # app.json_encoder.register(Event, lambda x: x.name)

    app.config['BROKER_AVAILABLE_EVENTS'] = [e.name for e in EVENTS]
    event_handlers = EVENT_HANDLERS_TEMPLATE.copy()

    # broker_rabbit = BrokerRabbit()
    # broker_rabbit.init_app(app, event_handlers)

    return event_handlers
