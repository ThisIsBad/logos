"""LogicBrain - Deterministic Logic Verifier.

A Z3-backed verifier for propositional and predicate logic.
Can be used directly by AI agents via Python execution.

Quick usage:
    >>> from logic_brain import verify
    >>> result = verify("P -> Q, P |- Q")
    >>> result.valid
    True
    >>> result.rule
    'Modus Ponens'
"""

from .models import Proposition, LogicalExpression, Connective, Argument, VerificationResult
from .verifier import PropositionalVerifier
from .predicate_models import (
    Variable, Constant, Predicate, PredicateConnective,
    PredicateExpression, QuantifiedExpression, Quantifier, FOLArgument
)
from .predicate import PredicateVerifier
from .parser import (
    verify,
    parse_argument,
    parse_expression,
    is_tautology,
    is_contradiction,
    are_equivalent,
    ParseError,
)
from .lean_session import LeanSession, TacticResult, is_lean_available
from .z3_session import Z3Session, CheckResult
from .diagnostics import (
    Diagnostic,
    ErrorType,
    LeanDiagnosticParser,
    Z3DiagnosticParser,
)

__all__ = [
    # Quick API (string-based)
    "verify",
    "parse_argument",
    "parse_expression",
    "is_tautology",
    "is_contradiction",
    "are_equivalent",
    "ParseError",
    # Core classes
    "Proposition",
    "LogicalExpression",
    "Connective",
    "Argument",
    "VerificationResult",
    "PropositionalVerifier",
    # FOL classes
    "Variable",
    "Constant",
    "Predicate",
    "PredicateConnective",
    "PredicateExpression",
    "QuantifiedExpression",
    "Quantifier",
    "FOLArgument",
    "PredicateVerifier",
    # Lean 4 interactive session
    "LeanSession",
    "TacticResult",
    "is_lean_available",
    # Z3 interactive session
    "Z3Session",
    "CheckResult",
    # Diagnostics
    "Diagnostic",
    "ErrorType",
    "LeanDiagnosticParser",
    "Z3DiagnosticParser",
]
