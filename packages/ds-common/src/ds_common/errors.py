class FetchError(Exception):
    """Raised when an external data source cannot be reached or returns an unusable response."""


class DegradedSection(Exception):
    """Sentinel: a section of output couldn't be assembled. The pipeline should record the
    reason and continue rather than aborting the whole run."""
