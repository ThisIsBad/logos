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
from .generator import ProblemGenerator, GeneratorConfig
from .certificate import ProofCertificate, certify, certify_z3_session, verify_certificate
from .assumptions import (
    AssumptionConsistency,
    AssumptionEntry,
    AssumptionKind,
    AssumptionSet,
    AssumptionStatus,
)
from .counterfactual import CounterfactualPlanner, PlanBranch, PlanResult, PlanState, VariableDecl
from .action_policy import (
    ActionPolicyEngine,
    ActionPolicyResult,
    ActionPolicyRule,
    PolicyDecision,
    PolicyViolationEvidence,
)
from .uncertainty import (
    ConfidenceLevel,
    ConfidenceRecord,
    EscalationDecision,
    EscalationResult,
    RiskLevel,
    UncertaintyCalibrator,
    UncertaintyPolicy,
    certificate_reference,
    resolve_certificate_reference,
)
from .proof_exchange import (
    ProofBundle,
    ProofExchangeNode,
    ProofExchangeResult,
    create_proof_bundle,
    verify_proof_bundle,
)
from .belief_graph import (
    BeliefEdge,
    BeliefEdgeType,
    BeliefGraph,
    BeliefNode,
    ContradictionExplanation,
)
from .goal_contract import (
    GoalContract,
    GoalContractDiagnostic,
    GoalContractResult,
    GoalContractStatus,
    build_branch_context,
    evaluate_goal_contract,
    verify_contract_preconditions_z3,
)
from .orchestrator import Claim, ClaimStatus, OrchestrationStatus, ProofOrchestrator

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
    # Problem generation
    "ProblemGenerator",
    "GeneratorConfig",
    # Proof certificates (Tier 2 / Provisional)
    "ProofCertificate",
    "certify",
    "certify_z3_session",
    "verify_certificate",
    # Assumption state kernel (Tier 2 / Provisional)
    "AssumptionKind",
    "AssumptionStatus",
    "AssumptionEntry",
    "AssumptionConsistency",
    "AssumptionSet",
    # Counterfactual planning (Tier 2 / Provisional)
    "VariableDecl",
    "PlanState",
    "PlanBranch",
    "PlanResult",
    "CounterfactualPlanner",
    # Action policy enforcement (Tier 2 / Provisional)
    "PolicyDecision",
    "ActionPolicyRule",
    "PolicyViolationEvidence",
    "ActionPolicyResult",
    "ActionPolicyEngine",
    # Uncertainty calibration (Tier 2 / Provisional)
    "ConfidenceLevel",
    "RiskLevel",
    "EscalationDecision",
    "ConfidenceRecord",
    "EscalationResult",
    "UncertaintyPolicy",
    "UncertaintyCalibrator",
    "certificate_reference",
    "resolve_certificate_reference",
    # Proof exchange protocol (Tier 2 / Provisional)
    "ProofExchangeNode",
    "ProofBundle",
    "ProofExchangeResult",
    "create_proof_bundle",
    "verify_proof_bundle",
    # Causal belief graph (Tier 2 / Provisional)
    "BeliefEdgeType",
    "BeliefNode",
    "BeliefEdge",
    "ContradictionExplanation",
    "BeliefGraph",
    # Goal contracts (Tier 2 / Provisional)
    "GoalContractStatus",
    "GoalContractDiagnostic",
    "GoalContract",
    "GoalContractResult",
    "build_branch_context",
    "evaluate_goal_contract",
    "verify_contract_preconditions_z3",
    # Proof orchestration (Tier 2 / Provisional)
    "ClaimStatus",
    "Claim",
    "OrchestrationStatus",
    "ProofOrchestrator",
]
