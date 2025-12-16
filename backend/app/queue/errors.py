class NonRetryableJobError(Exception):
    """Raise this for errors that should NOT be retried (bad input, unsupported file, etc.)."""

    pass
