# -*- coding: utf-8 -*-
from ._errors import LanguageError
from ._sorts import Sort


class Predicate(object) :

    def __init__(self, name, lang, *args ) :

        self._symbol = name # name, a string
        self._lang = lang # fol the symbol belongs to
        self._type = []

        # we validate the arguments now
        for k, a in enumerate(args) :
            if isinstance(type(a),Sort) :
                raise LanguageError("Predicate.__init__() : arguments need \
                to be of type 'Sort', {}-th argument '{}' is of type '{}''".format(k+1,a, type(a)))
            if self._lang != a.language  :
                raise LanguageError("Predicate.__init__(): {}-th argument \
                belongs to a different language".format(k+1))
            self._type.append(a)

    @property
    def symbol(self) :
        return self._symbol

    @property
    def signature(self) :
        return tuple([self.symbol] + [a.name for a in self.type] )

    @property
    def arity(self) :
        return len(self._type)

    @property
    def type(self) :
        for a in self._type :
            yield a

    def __str__(self) :
        return '{}({})'.format(self.symbol, ','.join([ a.name for a in self._type ]))

    def dump(self) :
        return dict(symbol=self.symbol, type = [a.name for a in self._type])

class Equality(Predicate) :

    def __init__(self, lang, *args ) :
        if len(args) < 2 or len(args) > 2 :
            raise LanguageError("Equality.__init__() : Equality predicate must \
            have arity of 2, list of arguments has length {}".format(len(args)))
        super(Equality,self).__init__('=', lang, *args)
