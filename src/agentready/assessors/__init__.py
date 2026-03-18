"""Assessor factory for centralized assessor creation.

Phase 1 Task 3: Consolidated from duplicated create_all_assessors() functions
across CLI modules (main.py, assess_batch.py, demo.py).
"""

from .base import BaseAssessor
from .code_quality import (
    CodeSmellsAssessor,
    CyclomaticComplexityAssessor,
    SemanticNamingAssessor,
    StructuredLoggingAssessor,
    TypeAnnotationsAssessor,
)
from .consistency import DocstringConsistencyAssessor
from .containers import ContainerSetupAssessor
from .documentation import (
    ArchitectureDecisionsAssessor,
    CLAUDEmdAssessor,
    ConciseDocumentationAssessor,
    InlineDocumentationAssessor,
    OpenAPISpecsAssessor,
    READMEAssessor,
)
from .security import DependencySecurityAssessor
from .structure import (
    IssuePRTemplatesAssessor,
    OneCommandSetupAssessor,
    SeparationOfConcernsAssessor,
    StandardLayoutAssessor,
)
from .stub_assessors import LockFilesAssessor  # Backwards compatibility alias
from .stub_assessors import (
    ConventionalCommitsAssessor,
    DependencyPinningAssessor,
    FileSizeLimitsAssessor,
    GitignoreAssessor,
    create_stub_assessors,
)
from .testing import (
    BranchProtectionAssessor,
    CICDPipelineVisibilityAssessor,
    PreCommitHooksAssessor,
    TestCoverageAssessor,
)

__all__ = [
    "create_all_assessors",
    "BaseAssessor",
    "DocstringConsistencyAssessor",
    "LockFilesAssessor",
]


def create_all_assessors() -> list[BaseAssessor]:
    """Create all 26 assessors for assessment.

    Centralized factory function to eliminate duplication across CLI commands.
    Returns all implemented and stub assessors.

    Returns:
        List of all assessor instances
    """
    assessors = [
        # Tier 1 Essential (6 assessors - up from 5)
        CLAUDEmdAssessor(),
        READMEAssessor(),
        TypeAnnotationsAssessor(),
        StandardLayoutAssessor(),
        DependencyPinningAssessor(),  # Renamed from LockFilesAssessor
        DependencySecurityAssessor(),  # NEW: Merged dependency_freshness + security_scanning
        # Tier 2 Critical (11 assessors - 8 implemented, 3 stubs)
        DocstringConsistencyAssessor(),  # NEW: Anti-gaming check (issue #340)
        TestCoverageAssessor(),
        PreCommitHooksAssessor(),
        ConventionalCommitsAssessor(),
        GitignoreAssessor(),
        OneCommandSetupAssessor(),
        FileSizeLimitsAssessor(),
        SeparationOfConcernsAssessor(),
        ConciseDocumentationAssessor(),
        InlineDocumentationAssessor(),
        CyclomaticComplexityAssessor(),  # Actually Tier 3, but including here
        # Tier 3 Important (7 implemented)
        ArchitectureDecisionsAssessor(),
        IssuePRTemplatesAssessor(),
        CICDPipelineVisibilityAssessor(),
        SemanticNamingAssessor(),
        StructuredLoggingAssessor(),
        OpenAPISpecsAssessor(),
        # Tier 4 Advanced (3 assessors)
        BranchProtectionAssessor(),
        CodeSmellsAssessor(),
        ContainerSetupAssessor(),  # NEW: Conditional (only if Dockerfile/Containerfile exists)
    ]

    # Add remaining stub assessors (currently none - all implemented or removed)
    assessors.extend(create_stub_assessors())

    return assessors
