"""Idempotently import official public policy metadata without resetting demo data."""

from seed_dev_data import seed_policy_documents


if __name__ == "__main__":
    seed_policy_documents()
