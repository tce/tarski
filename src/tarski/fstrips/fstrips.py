# -*- coding: utf-8 -*-
from enum import Enum
from typing import List

import tarski.errors as err
import tarski.fol as fol
from .errors import InvalidEffectError
from tarski.syntax import *
from .. import theories as tsk_theories

class UniversalEffect:
    """ A forall-effect """

    def __init__(self, variables, effects):
        self.variables = variables
        self.effects = effects

    def __str__(self):
        return "forall ({}) : ({})".format(self.variables, ', '.join(self.effects))

    __repr__ = __str__


class SingleEffect:
    def __init__(self, condition):
        self.condition = condition

    def __str__(self):
        return "({} -> {})".format(self.condition, self.tostring())

    __repr__ = __str__

    def tostring(self):
        raise NotImplementedError("To be subclassed")


class AddEffect(SingleEffect):
    def __init__(self, atom, condition=Tautology()):
        super().__init__(condition)
        self.atom = atom

    def tostring(self):
        return "ADD({})".format(self.atom)


class DelEffect(SingleEffect):
    def __init__(self, atom, condition=Tautology()):
        super().__init__(condition)
        self.atom = atom

    def tostring(self):
        return "DEL({})".format(self.atom)


class FunctionalEffect(SingleEffect):
    def __init__(self, lhs, rhs, condition=Tautology()):
        super().__init__(condition)
        self.lhs = lhs
        self.rhs = rhs
        self.check_well_formed()

    def check_well_formed(self):
        if not isinstance(self.lhs, CompoundTerm):
            msg = "Error declaring FunctionalEffect: {}\n Invalid effect expression: \
            left hand side '{}' needs to be a functional term!".format(self.tostring(), self.lhs)
            raise InvalidEffectError(self, msg)

        if not isinstance(self.rhs, Term):
            msg = "Error declaring FunctionalEffect: {}\n Invalid effect expression: \
            right hand side '{}' needs to be a functional term!".format(self.tostring(), self.rhs)
            raise InvalidEffectError(self, msg)

    def tostring(self):
        return "{} := {}".format(self.lhs, self.rhs)

class IncreaseEffect(FunctionalEffect):
    def check_well_formed(self):
        if not isinstance(self.lhs, CompoundTerm):
            msg = "Error declaring IncreaseEffect: {}\n Invalid effect expression: \
            left hand side '{}' needs to be a functional term!".format(self.tostring(), self.lhs)
            raise InvalidEffectError(self, msg)

        if not isinstance(self.rhs, Term) and type(self.rhs) not in [int, float]:
            msg = "Error declaring IncreaseEffect: {}\n Invalid increase expression: \
            right hand side '{}' needs to be a constant or functional term!".format(
                self.tostring(), self.lhs)
            raise InvalidEffectError(self, msg)


class OptimizationType(Enum):
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"

    def __str__(self):
        return self.value.lower()

class ProceduralEffect(SingleEffect):

    def __init__(self, input: List[CompoundTerm], output: List[CompoundTerm]):
        super().__init__(Tautology())
        self.input = input
        self.output = output

    def tostring(self):
        return "in: {}, out: {}".format( ','.join([str(x) for x in self.input]),\
            ','.join([str(x) for x in self.output]))

class ChoiceEffect(SingleEffect):

    def __init__(self, obj_type: OptimizationType, obj, variables: List[CompoundTerm], constraints=Tautology()):
        super().__init__(constraints)
        # MRJ: verify the effect is well formed
        self.obj = obj
        self.obj_type = obj_type
        self.variables = variables
        self.check_well_formed()

    def check_well_formed(self):
        if not isinstance(self.obj, CompoundTerm):
            msg = "Error declaring Choice Effect: {}\n Invalid objective expression: \
            expression to optimize needs to be a functional term!".format(self.tostring())
            raise InvalidEffectError(self, msg)

    def tostring(self):
        return "{} {}, vars: {} subject to: {}".format(self.obj_type, \
            self.obj, ','.join([str(x) for x in self.variables]), self.condition)



class LogicalEffect(SingleEffect):
    def __init__(self, phi, condition=Tautology()):
        super().__init__(condition)
        self.formula = phi

    def tostring(self):
        return "{}".format(self.formula)


class VectorisedEffect(SingleEffect):
    """
        Action effects that modify the denotation of a vector (tuple) of terms
    """


    def __init__(self, lhs, rhs, condition=Tautology()):
        super().__init__(condition)
        self.lhs = lhs
        self.rhs = rhs
        self.check_well_formed()

    def check_well_formed(self):
        if not hasattr(self.lhs, 'shape'):
            msg = "Error declaring VectorisedEffect, lhs needs needs to be\
                vector or matrix like"
            raise InvalidEffectError(self, msg)
        if self.lhs.shape[0] > 1:
            msg = "Error declaring VectorisedEffect, lhs needs needs to be\
                a vector in column order"
            raise InvalidEffectError(self, msg)
        if not hasattr(self.rhs, 'shape'):
            msg = "Error declaring VectorisedEffect, rhs needs needs to be\
                vector or matrix like"
            raise InvalidEffectError(self, msg)
        if self.lhs.shape == self.rhs.shape:
            msg = "Error declaring VectorisedEffect, lhs and rhs need to have\
                same dimensions"
            raise InvalidEffectError(self, msg)

class LinearEffect(SingleEffect):
    """
        Action effects that modify the denotation of a vector of (terms)  with
        the restriction of interactions between the expressions on the right hand
        side to be of the form:

            Ax + b
    """
    def __init__(self, y, A, x, b, condition=Tautology()):
        super().__init__(condition)
        self.y = y
        self.A = A
        self.x = x
        self.b = b
        self.check_well_formed()

    def check_well_formed(self):
        if not hasattr(self.y, 'shape'):
            msg = "Error declaring VectorisedEffect, y needs needs to be\
                vector or matrix like"
            raise InvalidEffectError(self, msg)
        if self.y.shape[0] > 1:
            msg = "Error declaring VectorisedEffect, y needs needs to be\
                a vector in column order"
            raise InvalidEffectError(self, msg)
        if not hasattr(self.x, 'shape'):
            msg = "Error declaring VectorisedEffect, x needs needs to be\
                vector or matrix like"
            raise InvalidEffectError(self, msg)
        if self.y.shape == self.x.shape:
            msg = "Error declaring VectorisedEffect, y and x need to have\
                same dimensions"
            raise InvalidEffectError(self, msg)

        if not hasattr(self.A, 'shape'):
            msg = "Error declaring VectorisedEffect, coefficients matrix A needs to be\
                vector or matrix like"
            raise InvalidEffectError(self, msg)
        if self.y.shape[1] == self.A.shape[0]:
            msg = "Error declaring VectorisedEffect, y and x need to have\
                same dimensions"
            raise InvalidEffectError(self, msg)

        if not hasattr(self.b, 'shape'):
            msg = "Error declaring VectorisedEffect, coefficient vector b needs needs to be\
                vector or matrix like"
            raise InvalidEffectError(self, msg)
        if self.x.shape == self.b.shape:
            msg = "Error declaring VectorisedEffect, x and b need to have\
                same dimensions"
            raise InvalidEffectError(self, msg)

class BlackBoxEffect(SingleEffect):
    """
        Black box functional effect
    """
    def __init__(self, lhs, f, condition=Tautology()):
        super().__init__(condition)
        self.lhs = lhs
        self.function = f
        self.check_well_formed()

    def tostring(self):
        return "{} := {}".format(self.lhs, 'some function')

    def check_well_formed(self):
        """
            This method verifies
        """
        if not hasattr(self.lhs, 'shape'):
            msg = "Error declaring BlackBoxEffect, lhs needs needs to be\
                vector or matrix like"
            raise InvalidEffectError(self, msg)
        if self.lhs.shape[1] > 1:
            msg = "Error declaring BlackBoxEffect, lhs needs needs to be\
                a vector in column order"
            raise InvalidEffectError(self, msg)

        self.function.bind_to_language(self.lhs[0, 0].language)
        for k, y in enumerate(self.lhs[:,0]):
            ys = TermReference(y)
            ok = TermReference(self.function.out_x[k].symbol)
            if ys != ok:
                msg = "Error declaring BlackBoxEffect, lhs {}-th symbol {} is not\
                matched by corresponding function output, {}".format(k, str(y), str(ok))
                raise InvalidEffectError(self, msg)



class OptimizationMetric:
    def __init__(self, opt_expression, opt_type):
        self.opt_expression = opt_expression
        self.opt_type = opt_type


def language(name="Unnamed FOL Language", theories=None):
    """ Create an FSTRIPS-oriented First-Order Language.
        This is a standard FOL with a few convenient add-ons.
    """
    # By default, when defining a FSTRIPS problem we use a FOL with equality
    theories = theories or [tsk_theories.Theory.EQUALITY]
    lang = tsk_theories.language(name, theories)
    lang.register_operator_handler("<<", Term, Term, FunctionalEffect)
    lang.register_operator_handler(">>", Term, Term, lambda lhs, rhs: FunctionalEffect(rhs, lhs))  # Inverted
    return lang
