"""
Activity Selection Scheduler
Greedy algorithm: pick maximum non-overlapping transactions using earliest-finish-time first.
"""

class Transaction:
    def __init__(self, txn_id, account_id, start, end, amount, description):
        self.txn_id = txn_id
        self.account_id = account_id
        self.start = start
        self.end = end
        self.amount = amount
        self.description = description

    def __repr__(self):
        return (f"Txn({self.txn_id}, Acc={self.account_id}, "
                f"[{self.start}-{self.end}], ${self.amount})")


def greedy_activity_selection(transactions):
    """
    Greedy Activity Selection:
    Sort by finish time, then greedily pick each transaction that
    starts at or after the last selected transaction finishes.
    Returns the maximum set of non-overlapping transactions.
    """
    if not transactions:
        return []

    # Sort by finish time (greedy choice)
    sorted_txns = sorted(transactions, key=lambda t: t.end)

    selected = [sorted_txns[0]]
    last_end = sorted_txns[0].end

    for txn in sorted_txns[1:]:
        if txn.start >= last_end:   # non-overlapping
            selected.append(txn)
            last_end = txn.end

    return selected


def schedule_account_transactions(all_transactions, account_id, time_window=(0, 24)):
    """
    Schedule transactions for a specific account within a time window.
    """
    win_start, win_end = time_window
    # Filter for this account and within window
    candidates = [
        t for t in all_transactions
        if t.account_id == account_id
        and t.start >= win_start
        and t.end <= win_end
    ]
    return greedy_activity_selection(candidates)


def print_schedule_result(account_id, all_txns, selected, time_window):
    candidates = [
        t for t in all_txns
        if t.account_id == account_id
        and t.start >= time_window[0]
        and t.end <= time_window[1]
    ]
    print(f"\n{'='*60}")
    print(f"  Account {account_id} — Time Window {time_window}")
    print(f"{'='*60}")
    print(f"  Total requests : {len(candidates)}")
    print(f"  Scheduled      : {len(selected)}")
    print(f"\n  Rejected transactions (conflict):")
    rejected = [t for t in candidates if t not in selected]
    if rejected:
        for t in sorted(rejected, key=lambda x: x.start):
            print(f"    ✗ {t}")
    else:
        print("    None — all fit!")
    print(f"\n  Scheduled transactions (non-overlapping):")
    for t in selected:
        print(f"    ✓ {t}  | {t.description}")
    total = sum(t.amount for t in selected)
    print(f"\n  Total amount processed: ${total:,.2f}")


# ── Demo Data ──────────────────────────────────────────────────────────────
SAMPLE_TRANSACTIONS = [
    # Account A001
    Transaction("T01", "A001",  0,  3, 1500, "Payroll deposit"),
    Transaction("T02", "A001",  2,  5,  800, "Vendor payment"),   # overlaps T01
    Transaction("T03", "A001",  5,  8, 2000, "Loan installment"),
    Transaction("T04", "A001",  6, 10,  500, "Utility bill"),      # overlaps T03
    Transaction("T05", "A001",  9, 12, 1200, "Transfer to savings"),
    Transaction("T06", "A001", 11, 14,  300, "Insurance premium"), # overlaps T05
    Transaction("T07", "A001", 14, 17,  750, "Stock purchase"),
    Transaction("T08", "A001", 16, 19,  900, "Subscription fee"),  # overlaps T07
    Transaction("T09", "A001", 19, 22, 4000, "Rent payment"),
    Transaction("T10", "A001", 21, 24,  100, "Tip transfer"),      # overlaps T09

    # Account A002
    Transaction("T11", "A002",  1,  4,  600, "E-commerce refund"),
    Transaction("T12", "A002",  3,  7, 1100, "Freelance payment"),
    Transaction("T13", "A002",  6,  9,  200, "ATM withdrawal"),
    Transaction("T14", "A002",  8, 11,  350, "Coffee subscription"),
    Transaction("T15", "A002", 10, 13, 2500, "Consulting invoice"),
    Transaction("T16", "A002", 12, 15,  800, "Travel booking"),    # overlaps T15
    Transaction("T17", "A002", 15, 18,  450, "Grocery payment"),
    Transaction("T18", "A002", 17, 20, 1000, "Medical bill"),      # overlaps T17
    Transaction("T19", "A002", 20, 22,  300, "Gym membership"),
    Transaction("T20", "A002", 21, 24,  700, "Dinner transfer"),   # overlaps T19
]


def run_activity_selection_demo():
    print("\n" + "█"*60)
    print("  GREEDY ACTIVITY SELECTION — Transaction Scheduler")
    print("█"*60)

    for acc in ["A001", "A002"]:
        selected = schedule_account_transactions(SAMPLE_TRANSACTIONS, acc, (0, 24))
        print_schedule_result(acc, SAMPLE_TRANSACTIONS, selected, (0, 24))

    print("\n" + "─"*60)
    print("  GREEDY CORRECTNESS NOTE")
    print("─"*60)
    print("  Strategy : Sort by finish time → always pick earliest-ending")
    print("             non-overlapping transaction.")
    print("  Optimality: At each step, choosing the earliest-finishing")
    print("             transaction leaves the maximum remaining window,")
    print("             which is provably optimal (exchange argument).")


if __name__ == "__main__":
    run_activity_selection_demo()