"""Tests for docstring-signature consistency assessor."""

import subprocess

from agentready.assessors.consistency import DocstringConsistencyAssessor
from agentready.models.repository import Repository


def _make_repo(tmp_path, languages=None):
    """Create a minimal Repository for testing."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    return Repository(
        path=tmp_path,
        name="test-repo",
        url=None,
        branch="main",
        commit_hash="abc123",
        languages=languages or {"Python": 100},
        total_files=10,
        total_lines=100,
    )


class TestDocstringConsistencyAssessor:
    """Test DocstringConsistencyAssessor."""

    def test_not_applicable_non_python(self, tmp_path):
        """Test that assessor is not applicable for non-Python repos."""
        repo = _make_repo(tmp_path, languages={"JavaScript": 100})
        assessor = DocstringConsistencyAssessor()
        assert not assessor.is_applicable(repo)

    def test_applicable_python(self, tmp_path):
        """Test that assessor is applicable for Python repos."""
        repo = _make_repo(tmp_path, languages={"Python": 100})
        assessor = DocstringConsistencyAssessor()
        assert assessor.is_applicable(repo)

    def test_no_documented_functions(self, tmp_path):
        """Test not_applicable when no functions have Args docstrings."""
        (tmp_path / "main.py").write_text(
            'def hello():\n    """Say hello."""\n    print("hello")\n'
        )
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)
        assert finding.status == "not_applicable"

    def test_consistent_docstrings_pass(self, tmp_path):
        """Test that consistent docstrings score high."""
        (tmp_path / "service.py").write_text('''
def create_order(customer_name: str, total: float) -> dict:
    """Create a new order.

    Args:
        customer_name: Name of the customer.
        total: Order total in USD.

    Returns:
        The created order dict.
    """
    return {"name": customer_name, "total": total}


def get_order(order_id: int) -> dict:
    """Fetch an order by ID.

    Args:
        order_id: The order primary key.

    Returns:
        Order dict if found.
    """
    return {"id": order_id}
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_phantom_params_fail(self, tmp_path):
        """Test that docstrings documenting non-existent params are flagged."""
        (tmp_path / "service.py").write_text('''
class OrderService:
    def __init__(self):
        """Initialize with database session, cache, and event bus.

        Args:
            session: SQLAlchemy async session (injected).
            cache: Redis client for order caching (injected).
            event_bus: Domain event publisher (injected).
        """
        pass
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "fail"
        assert finding.score == 0.0
        assert any("documented but not in signature" in e for e in finding.evidence)
        assert finding.remediation is not None

    def test_undocumented_params_fail(self, tmp_path):
        """Test that params in signature but missing from docstring are flagged."""
        (tmp_path / "service.py").write_text('''
def process(data: dict, timeout: int, retries: int) -> bool:
    """Process data.

    Args:
        data: Input data dictionary.
    """
    return True
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "fail"
        assert any("in signature but not documented" in e for e in finding.evidence)

    def test_mixed_consistency(self, tmp_path):
        """Test partial consistency gives proportional score."""
        (tmp_path / "service.py").write_text('''
def good_func(x: int, y: int) -> int:
    """Add two numbers.

    Args:
        x: First number.
        y: Second number.
    """
    return x + y


def bad_func(a: str) -> str:
    """Transform string.

    Args:
        a: Input string.
        b: Another string.
        c: Yet another.
    """
    return a.upper()


def also_good(name: str) -> str:
    """Greet someone.

    Args:
        name: The person to greet.
    """
    return f"Hello {name}"
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        # 2 out of 3 consistent = 66.7%, proportional score = 83.3 (passes ≥75)
        assert finding.status == "pass"
        assert 80 < finding.score < 90

    def test_sphinx_style_docstrings(self, tmp_path):
        """Test that Sphinx-style docstrings are parsed."""
        (tmp_path / "module.py").write_text('''
def connect(host: str, port: int) -> bool:
    """Connect to a server.

    :param host: The hostname.
    :param port: The port number.
    :returns: True if connected.
    """
    return True
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_numpy_style_docstrings(self, tmp_path):
        """Test that NumPy-style docstrings are parsed."""
        (tmp_path / "module.py").write_text('''
def transform(data: list, scale: float) -> list:
    """Transform data by scaling.

    Parameters
    ----------
    data : list
        Input data.
    scale : float
        Scale factor.

    Returns
    -------
    list
        Scaled data.
    """
    return [x * scale for x in data]
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_async_functions_checked(self, tmp_path):
        """Test that async function definitions are also checked."""
        (tmp_path / "async_service.py").write_text('''
async def fetch_data(url: str, timeout: int) -> dict:
    """Fetch data from URL.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.
    """
    return {}
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_kwargs_and_args_handled(self, tmp_path):
        """Test that *args and **kwargs are handled correctly."""
        (tmp_path / "module.py").write_text('''
def flexible(name: str, *args, **kwargs) -> None:
    """Do something flexible.

    Args:
        name: The name.
        args: Positional arguments.
        kwargs: Keyword arguments.
    """
    pass
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"

    def test_kwonly_args_handled(self, tmp_path):
        """Test that keyword-only arguments are checked."""
        (tmp_path / "module.py").write_text('''
def strict(name: str, *, verbose: bool = False) -> None:
    """Do something strictly.

    Args:
        name: The name.
        verbose: Enable verbose output.
    """
    pass
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"

    def test_self_cls_excluded(self, tmp_path):
        """Test that self and cls are excluded from comparison."""
        (tmp_path / "module.py").write_text('''
class Foo:
    def method(self, x: int) -> int:
        """Do something.

        Args:
            x: Input value.
        """
        return x

    @classmethod
    def create(cls, name: str) -> "Foo":
        """Create instance.

        Args:
            name: Instance name.
        """
        return cls()
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_syntax_error_files_skipped(self, tmp_path):
        """Test that files with syntax errors are gracefully skipped."""
        (tmp_path / "good.py").write_text('''
def good(x: int) -> int:
    """Good function.

    Args:
        x: Input.
    """
    return x
''')
        (tmp_path / "bad.py").write_text("def broken(\n")  # syntax error

        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        # Should still assess the good file
        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_google_style_with_type_in_parens(self, tmp_path):
        """Test Google-style docstrings with type annotations in parens."""
        (tmp_path / "module.py").write_text('''
def process(data, count):
    """Process data items.

    Args:
        data (dict): The data to process.
        count (int): Number of items.
    """
    pass
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_positional_only_params(self, tmp_path):
        """Test that positional-only parameters (before /) are checked."""
        (tmp_path / "module.py").write_text('''
def lookup(key, /, default=None):
    """Look up a value.

    Args:
        key: The lookup key.
        default: Fallback value.
    """
    return default
''')
        repo = _make_repo(tmp_path)
        assessor = DocstringConsistencyAssessor()
        finding = assessor.assess(repo)

        assert finding.status == "pass"
        assert finding.score == 100.0

    def test_attribute_properties(self):
        """Test assessor attribute properties."""
        assessor = DocstringConsistencyAssessor()
        assert assessor.attribute_id == "docstring_consistency"
        assert assessor.tier == 2
        assert assessor.attribute.default_weight == 0.02
