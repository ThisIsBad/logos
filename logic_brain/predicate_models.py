"""Data models for First-Order Logic (Predicate Logic)."""

from dataclasses import dataclass
from enum import Enum
from typing import Union

class Quantifier(Enum):
    FORALL = "∀"
    EXISTS = "∃"

@dataclass(frozen=True)
class Variable:
    """A logical variable (e.g., x, y)."""
    name: str
    
    def __str__(self):
        return self.name

@dataclass(frozen=True)
class Constant:
    """A specific entity/constant (e.g., Socrates, John)."""
    name: str
    
    def __str__(self):
        return self.name

Term = Union[Variable, Constant]

@dataclass(frozen=True)
class Predicate:
    """A predicate applied to terms (e.g., Mortal(Socrates), Loves(x, y))."""
    name: str
    terms: tuple[Term, ...]
    
    def __str__(self):
        terms_str = ", ".join(str(t) for t in self.terms)
        return f"{self.name}({terms_str})"

class PredicateConnective(Enum):
    NOT = "¬"
    AND = "∧"
    OR = "∨"
    IMPLIES = "→"
    IFF = "↔"

@dataclass(frozen=True)
class PredicateExpression:
    """A compound expression in predicate logic."""
    connective: PredicateConnective
    left: 'FOLFormula'
    right: 'FOLFormula' = None  # None for NOT
    
    def __str__(self):
        if self.connective == PredicateConnective.NOT:
            return f"{self.connective.value}{self.left}"
        return f"({self.left} {self.connective.value} {self.right})"

@dataclass(frozen=True)
class QuantifiedExpression:
    """An expression bound by a quantifier."""
    quantifier: Quantifier
    variable: Variable
    expression: 'FOLFormula'
    
    def __str__(self):
        return f"{self.quantifier.value}{self.variable.name} {self.expression}"

FOLFormula = Union[Predicate, PredicateExpression, QuantifiedExpression]

@dataclass(frozen=True)
class FOLArgument:
    """An argument consisting of premises and a conclusion in First-Order Logic."""
    premises: tuple[FOLFormula, ...]
    conclusion: FOLFormula
    
    def __str__(self):
        lines = ["Premises:"]
        for i, p in enumerate(self.premises, 1):
            lines.append(f"  {i}. {p}")
        lines.append(f"Conclusion: {self.conclusion}")
        return "\n".join(lines)
