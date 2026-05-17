from __future__ import annotations

try:
    from tenacity import retry, stop_after_attempt, wait_exponential
except ModuleNotFoundError:  # pragma: no cover - requirements.txt provides tenacity
    retry = None
    stop_after_attempt = None
    wait_exponential = None


def retryable(attempts: int = 3, min_wait: int = 4, max_wait: int = 10):
    if retry is None:
        def decorator(function):
            return function

        return decorator
    return retry(stop=stop_after_attempt(attempts), wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait))
