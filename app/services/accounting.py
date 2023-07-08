from typing import List

from app.models.base import Transaction


def distribute(
    target: Transaction, sources: List[Transaction]
) -> List[Transaction]:
    dirty = []
    for source in sources:
        increment = min(target.remainder(), source.remainder())
        if increment == 0:
            break
        for transaction in [source, target]:
            transaction.invested_amount += increment
            if transaction.invested_amount == transaction.full_amount:
                transaction.complete()
        dirty.append(source)
    return dirty
