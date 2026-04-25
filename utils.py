def calculate_balances(members, expenses):
    balances = {m: 0 for m in members}

    for exp in expenses:
        split = exp.amount / len(members)

        for m in members:
            balances[m] -= split

        balances[exp.paid_by] += exp.amount

    return balances