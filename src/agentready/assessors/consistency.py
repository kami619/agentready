"""Docstring-signature consistency assessor.

Detects mismatches between function signatures and their docstrings,
catching cases where documentation claims (e.g., dependency injection
parameters) don't match actual code. This directly addresses gaming
where repos score high on documentation presence while the docs are
misleading. See: https://github.com/ambient-code/agentready/issues/340
"""

import ast
import logging
import re

from ..models.attribute import Attribute
from ..models.finding import Citation, Finding, Remediation
from ..models.repository import Repository
from ..utils.subprocess_utils import safe_subprocess_run
from .base import BaseAssessor

logger = logging.getLogger(__name__)


class DocstringConsistencyAssessor(BaseAssessor):
    """Assesses whether function docstrings match their actual signatures.

    Tier 2 Critical (2% weight) - Misleading docstrings actively harm AI agents
    by causing them to generate incorrect code (e.g., calling constructors with
    parameters that don't exist).
    """

    @property
    def attribute_id(self) -> str:
        return "docstring_consistency"

    @property
    def tier(self) -> int:
        return 2  # Critical

    @property
    def attribute(self) -> Attribute:
        return Attribute(
            id=self.attribute_id,
            name="Docstring-Signature Consistency",
            category="Code Quality",
            tier=self.tier,
            description="Function docstrings accurately reflect actual signatures",
            criteria="≥80% of documented functions have consistent docstring-signature pairs",
            default_weight=0.02,
        )

    def is_applicable(self, repository: Repository) -> bool:
        """Only applicable to Python repositories (docstring conventions)."""
        return "Python" in repository.languages

    def assess(self, repository: Repository) -> Finding:
        """Check docstring-signature consistency across Python files."""
        try:
            result = safe_subprocess_run(
                ["git", "ls-files", "*.py"],
                cwd=repository.path,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            python_files = [f for f in result.stdout.strip().split("\n") if f]
        except Exception:
            python_files = []

        if not python_files:
            python_files = [
                str(f.relative_to(repository.path))
                for f in repository.path.rglob("*.py")
            ]

        total_documented = 0
        consistent_count = 0
        mismatches: list[str] = []

        for file_path in python_files:
            full_path = repository.path / file_path
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content, filename=str(file_path))
                file_results = self._check_file(tree, str(file_path))

                total_documented += file_results["documented"]
                consistent_count += file_results["consistent"]
                mismatches.extend(file_results["mismatches"])

            except (OSError, UnicodeDecodeError, SyntaxError):
                continue

        if total_documented == 0:
            return Finding.not_applicable(
                self.attribute,
                reason="No Python functions with Args docstrings found",
            )

        consistency_pct = (consistent_count / total_documented) * 100
        score = self.calculate_proportional_score(
            measured_value=consistency_pct,
            threshold=80.0,
            higher_is_better=True,
        )

        status = "pass" if score >= 75 else "fail"

        evidence = [
            f"Consistent: {consistent_count}/{total_documented} documented functions ({consistency_pct:.1f}%)",
        ]

        # Show up to 5 mismatches as evidence
        for mismatch in mismatches[:5]:
            evidence.append(mismatch)

        if len(mismatches) > 5:
            evidence.append(f"... and {len(mismatches) - 5} more mismatches")

        return Finding(
            attribute=self.attribute,
            status=status,
            score=score,
            measured_value=f"{consistency_pct:.1f}%",
            threshold="≥80%",
            evidence=evidence,
            remediation=self._create_remediation() if status == "fail" else None,
            error_message=None,
        )

    def _check_file(self, tree: ast.AST, file_path: str) -> dict[str, int | list[str]]:
        """Check all functions/methods in a single file.

        Returns dict with documented count, consistent count, and mismatch descriptions.
        """
        documented = 0
        consistent = 0
        mismatches: list[str] = []

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            docstring = ast.get_docstring(node)
            if not docstring:
                continue

            doc_params = self._parse_docstring_params(docstring)
            if not doc_params:
                # Docstring exists but has no Args section — not checkable
                continue

            documented += 1

            sig_params = self._get_signature_params(node)
            is_consistent, detail = self._compare_params(
                sig_params, doc_params, node.name, file_path, node.lineno
            )

            if is_consistent:
                consistent += 1
            else:
                mismatches.append(detail)

        return {
            "documented": documented,
            "consistent": consistent,
            "mismatches": mismatches,
        }

    def _get_signature_params(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[str]:
        """Extract parameter names from function signature, excluding self/cls."""
        params = []
        # Positional-only params (before / in signature)
        for arg in node.args.posonlyargs:
            if arg.arg not in ("self", "cls"):
                params.append(arg.arg)
        for arg in node.args.args:
            if arg.arg not in ("self", "cls"):
                params.append(arg.arg)
        # Also include *args and **kwargs if present
        if node.args.vararg:
            params.append(node.args.vararg.arg)
        if node.args.kwarg:
            params.append(node.args.kwarg.arg)
        # keyword-only args
        for arg in node.args.kwonlyargs:
            params.append(arg.arg)
        return params

    def _parse_docstring_params(self, docstring: str) -> list[str]:
        """Extract parameter names from docstring Args section.

        Supports Google-style, NumPy-style, and Sphinx-style docstrings.
        """
        params: list[str] = []

        # Google-style: "Args:\n    param_name: description"
        # Also matches "Arguments:"
        google_match = re.search(r"(?:Args|Arguments)\s*:\s*\n", docstring)
        if google_match:
            # Extract the indented block after "Args:"
            remainder = docstring[google_match.end() :]
            for line in remainder.split("\n"):
                # Stop at blank lines or new section headers (non-indented lines)
                if not line or not line[0].isspace():
                    break
                stripped = line.strip()
                if not stripped:
                    break
                # Parameter line: "param_name (type): description" or "param_name: description"
                param_match = re.match(r"(\w+)\s*(?:\(.*?\))?\s*:", stripped)
                if param_match:
                    params.append(param_match.group(1))
            return params

        # Sphinx-style: ":param param_name:" or ":type param_name:"
        sphinx_params = re.findall(r":param\s+(\w+)\s*:", docstring)
        if sphinx_params:
            return list(dict.fromkeys(sphinx_params))  # deduplicate, preserve order

        # NumPy-style: "Parameters\n----------\nparam_name : type"
        numpy_match = re.search(
            r"Parameters\s*\n\s*-+\s*\n((?:.*\n?)*?)(?:\n\s*\n|\Z)",
            docstring,
        )
        if numpy_match:
            params_block = numpy_match.group(1)
            for line in params_block.split("\n"):
                stripped = line.strip()
                if not stripped or stripped.startswith("-"):
                    continue
                param_match = re.match(r"(\w+)\s*:", stripped)
                if param_match:
                    params.append(param_match.group(1))
            return params

        return params

    def _compare_params(
        self,
        sig_params: list[str],
        doc_params: list[str],
        func_name: str,
        file_path: str,
        lineno: int,
    ) -> tuple[bool, str]:
        """Compare signature params against documented params.

        Returns (is_consistent, detail_string).
        """
        sig_set = set(sig_params)
        doc_set = set(doc_params)

        undocumented = sig_set - doc_set
        phantom = doc_set - sig_set

        if not undocumented and not phantom:
            return True, ""

        parts = []
        if phantom:
            parts.append(
                f"documented but not in signature: {', '.join(sorted(phantom))}"
            )
        if undocumented:
            parts.append(
                f"in signature but not documented: {', '.join(sorted(undocumented))}"
            )

        detail = f"{file_path}:{lineno} {func_name}() — {'; '.join(parts)}"
        return False, detail

    def _create_remediation(self) -> Remediation:
        """Create remediation guidance for docstring inconsistencies."""
        return Remediation(
            summary="Fix docstrings to match actual function signatures",
            steps=[
                "Run a docstring linter to find mismatches (e.g., pydocstyle, darglint, ruff D rules)",
                "Update docstring Args sections to list only the parameters the function actually accepts",
                "Remove references to parameters that don't exist in the signature",
                "Add documentation for parameters that are in the signature but missing from docstrings",
                "Pay special attention to __init__ methods — ensure documented params match constructor signature",
            ],
            tools=["pydocstyle", "darglint", "ruff"],
            commands=[
                "# Check docstring style",
                "pip install pydocstyle",
                "pydocstyle src/",
                "",
                "# Use ruff for docstring checks",
                "ruff check --select D src/",
            ],
            examples=[
                """# BAD: Docstring claims 3 params, constructor takes 0
class OrderService:
    def __init__(self):
        \\"\\"\\"Initialize service.

        Args:
            session: Database session.     # LIE - not in signature
            cache: Redis client.           # LIE - not in signature
            event_bus: Event publisher.     # LIE - not in signature
        \\"\\"\\"
        pass

# GOOD: Docstring matches signature
class OrderService:
    def __init__(self, session: Session, cache: Redis, event_bus: EventBus):
        \\"\\"\\"Initialize service.

        Args:
            session: Database session.
            cache: Redis client.
            event_bus: Event publisher.
        \\"\\"\\"
        self.session = session
        self.cache = cache
        self.event_bus = event_bus
""",
            ],
            citations=[
                Citation(
                    source="GitHub",
                    title="AgentReady Audit - Gaming with misleading docstrings",
                    url="https://github.com/ugiordan/agentready-audit",
                    relevance="Proof-of-concept showing how misleading docstrings game AI readiness scores",
                ),
                Citation(
                    source="PEP 257",
                    title="Docstring Conventions",
                    url="https://peps.python.org/pep-0257/",
                    relevance="Python docstring conventions and best practices",
                ),
            ],
        )
