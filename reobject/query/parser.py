import operator
from functools import reduce

from reobject.utils import cmp


class _Q(object):
    verbs = (
        'contains', 'endswith', 'gt', 'gte', 'in', 'isnull', 'lt', 'lte',
        'startswith'
    )

    def __init__(self, **kwargs):
        if kwargs:
            attr, self.value = list(kwargs.items())[0]

            if attr.rsplit('__', 1)[-1] in self.verbs:
                self.attr, self.verb = attr.rsplit('__', 1)
            else:
                self.attr = attr
                self.verb = None

            self.comparator = self._comparator_func
        else:
            self.comparator = lambda x: True

    def _comparator_func(self, obj):
        (value,) = cmp(self.attr)(obj)

        if self.verb:
            return self.apply_verb(value)
        else:
            return value == self.value

    def __and__(self, other):
        new = type(self)()
        new.comparator = lambda obj: self.comparator(obj) and \
                                     other.comparator(obj)
        return new

    def __or__(self, other):
        new = type(self)()
        new.comparator = lambda obj: self.comparator(obj) or \
                                     other.comparator(obj)
        return new

    def __invert__(self):
        new = type(self)()
        new.comparator = lambda obj: not self.comparator(obj)
        return new

    def apply_verb(self, value):
        if self.verb == 'contains':
            return self.value in value
        elif self.verb == 'endswith':
            return value.endswith(self.value)
        elif self.verb == 'gt':
            return value > self.value
        elif self.verb == 'gte':
            return value >= self.value
        elif self.verb == 'in':
            return value in self.value
        elif self.verb == 'isnull':
            return not value
        elif self.verb == 'lt':
            return value < self.value
        elif self.verb == 'lte':
            return value <= self.value
        elif self.verb == 'startswith':
            return value.startswith(self.value)


class Q(object):
    def __new__(cls, *args, **kwargs):
        return reduce(
            operator.and_,
            map(lambda k: _Q(**{k: kwargs[k]}), kwargs),
            _Q()
        )
