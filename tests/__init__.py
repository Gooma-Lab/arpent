"""Makes ``tests`` an importable package.

Needed so one test module can reuse another's helpers — the provider contract
lives in ``test_provider`` and is inherited by every implementation's suite.
"""
