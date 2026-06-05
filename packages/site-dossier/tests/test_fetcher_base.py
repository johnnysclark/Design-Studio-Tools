from site_dossier.fetchers.base import degrade_on_failure
from site_dossier.models import FetcherResult


def test_degrade_returns_result_on_exception():
    @degrade_on_failure("widgets")
    def broken() -> FetcherResult:
        raise RuntimeError("api down")

    result = broken()
    assert isinstance(result, FetcherResult)
    assert result.status == "unavailable"
    assert result.source == "widgets"
    assert "api down" in result.notes[0]


def test_degrade_passes_through_success():
    expected = FetcherResult(status="ok", source="x", data={"k": 1})

    @degrade_on_failure("widgets")
    def works() -> FetcherResult:
        return expected

    assert works() is expected
