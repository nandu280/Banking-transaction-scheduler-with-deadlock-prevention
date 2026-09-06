"""
Banker's Algorithm — Deadlock Prevention
Accounts are "processes", fund types are "resource types".
Before approving a transfer request, run the safety check.
"""

class BankersAlgorithm:
    """
    Implements the Banker's Algorithm.

    accounts    : list of account names
    fund_types  : list of resource/fund type names
    total       : total available units per fund type  (1-D list)
    allocation  : currently allocated per account      (2-D list)
    max_need    : maximum need per account             (2-D list)
    """

    def __init__(self, accounts, fund_types, total, allocation, max_need):
        self.accounts   = accounts
        self.fund_types = fund_types
        self.n          = len(accounts)        # number of accounts
        self.m          = len(fund_types)      # number of fund types
        self.total      = list(total)
        self.allocation = [list(row) for row in allocation]
        self.max_need   = [list(row) for row in max_need]

        # need[i][j] = max_need[i][j] - allocation[i][j]
        self.need = [
            [self.max_need[i][j] - self.allocation[i][j]
             for j in range(self.m)]
            for i in range(self.n)
        ]

        # available = total - sum(allocation for each account)
        self.available = list(total)
        for i in range(self.n):
            for j in range(self.m):
                self.available[j] -= self.allocation[i][j]

    # ── helpers ────────────────────────────────────────────────────────────

    def _can_satisfy(self, need_row, available):
        return all(need_row[j] <= available[j] for j in range(self.m))

    def _fmt_vec(self, vec):
        return "[" + ", ".join(f"{v:4d}" for v in vec) + "]"

    # ── safety algorithm ───────────────────────────────────────────────────

    def is_safe(self, alloc=None, avail=None, verbose=False):
        """
        Run the safety algorithm on the given (or current) state.
        Returns (safe: bool, safe_sequence: list).
        """
        if alloc is None:
            alloc = [row[:] for row in self.allocation]
        if avail is None:
            avail = self.available[:]

        need = [
            [self.max_need[i][j] - alloc[i][j] for j in range(self.m)]
            for i in range(self.n)
        ]

        work    = avail[:]
        finish  = [False] * self.n
        sequence = []

        if verbose:
            print(f"\n    Safety Check — Available: {self._fmt_vec(work)}")

        while True:
            found = False
            for i in range(self.n):
                if not finish[i] and self._can_satisfy(need[i], work):
                    # Simulate completion: release its allocation
                    for j in range(self.m):
                        work[j] += alloc[i][j]
                    finish[i] = True
                    sequence.append(self.accounts[i])
                    found = True
                    if verbose:
                        print(f"    → {self.accounts[i]} can proceed; "
                              f"work becomes {self._fmt_vec(work)}")
                    break   # restart scan after each selection
            if not found:
                break

        safe = all(finish)
        return safe, sequence

    # ── request handling ───────────────────────────────────────────────────

    def request_resources(self, account_name, request, verbose=True):
        """
        Try to grant a resource request for account_name.
        request : list of requested units per fund type.
        Returns dict with outcome details.
        """
        i = self.accounts.index(account_name)

        header = f"\n{'─'*60}\n  REQUEST: {account_name} asks {self._fmt_vec(request)}\n{'─'*60}"
        if verbose:
            print(header)

        # Step 1: request <= need?
        for j in range(self.m):
            if request[j] > self.need[i][j]:
                msg = (f"  ✗ REJECTED — {account_name} exceeds its declared "
                       f"max need on {self.fund_types[j]}. "
                       f"(request={request[j]}, need={self.need[i][j]})")
                if verbose:
                    print(msg)
                return {"approved": False, "reason": msg, "account": account_name,
                        "request": request}

        # Step 2: request <= available?
        for j in range(self.m):
            if request[j] > self.available[j]:
                msg = (f"  ✗ REJECTED — Insufficient funds available for "
                       f"{self.fund_types[j]}. "
                       f"(request={request[j]}, available={self.available[j]})")
                if verbose:
                    print(msg)
                return {"approved": False, "reason": msg, "account": account_name,
                        "request": request}

        # Step 3: Tentatively allocate, check safety
        for j in range(self.m):
            self.available[j]      -= request[j]
            self.allocation[i][j]  += request[j]
            self.need[i][j]        -= request[j]

        safe, seq = self.is_safe(verbose=verbose)

        if safe:
            msg = (f"  ✓ APPROVED — Safe sequence found: "
                   f"{' → '.join(seq)}")
            if verbose:
                print(msg)
            return {"approved": True, "reason": msg, "account": account_name,
                    "request": request, "safe_sequence": seq}
        else:
            # Rollback
            for j in range(self.m):
                self.available[j]      += request[j]
                self.allocation[i][j]  -= request[j]
                self.need[i][j]        += request[j]
            msg = (f"  ✗ REJECTED — Would create UNSAFE state (deadlock risk). "
                   f"Request rolled back.")
            if verbose:
                print(msg)
            # Suggest modification
            suggestion = self._suggest_safe_request(i, request)
            if suggestion and verbose:
                print(f"  💡 SUGGESTION: Try requesting {self._fmt_vec(suggestion)} instead.")
            return {"approved": False, "reason": msg, "account": account_name,
                    "request": request, "suggestion": suggestion}

    # ── bonus: suggest smallest safe request ──────────────────────────────

    def _suggest_safe_request(self, acc_idx, request):
        """
        Binary-search-style: try reducing the request by 1 unit on the
        most-constrained fund type until a safe state is found.
        Simple heuristic — not guaranteed globally optimal but practical.
        """
        suggestion = request[:]
        for j in range(self.m):
            original = suggestion[j]
            for reduced in range(original - 1, -1, -1):
                suggestion[j] = reduced
                # Tentative allocation
                ok = True
                for jj in range(self.m):
                    if suggestion[jj] > self.available[jj]:
                        ok = False
                        break
                if not ok:
                    continue
                # Simulate
                alloc_copy = [row[:] for row in self.allocation]
                avail_copy = self.available[:]
                for jj in range(self.m):
                    alloc_copy[acc_idx][jj] += suggestion[jj]
                    avail_copy[jj]          -= suggestion[jj]
                safe, _ = self.is_safe(alloc_copy, avail_copy)
                if safe:
                    return suggestion
            suggestion[j] = original   # restore if no reduction helped
        return None

    # ── display ────────────────────────────────────────────────────────────

    def print_state(self):
        col = 6
        hdr = f"{'Account':<10}"
        for ft in self.fund_types:
            hdr += f"  {ft[:col]:>{col}}"
        sep = "─" * len(hdr)

        def row(label, vec):
            s = f"{label:<10}"
            for v in vec:
                s += f"  {v:{col}d}"
            return s

        print(f"\n{'='*60}")
        print("  BANKER'S ALGORITHM — System State")
        print(f"{'='*60}")
        print(f"\n  Total Resources  : {self._fmt_vec(self.total)}")
        print(f"  Available        : {self._fmt_vec(self.available)}")

        print(f"\n  {hdr}")
        print(f"  {sep}")
        for i, acc in enumerate(self.accounts):
            print(f"  Alloc  {row(acc, self.allocation[i])}")
            print(f"  Max    {row(acc, self.max_need[i])}")
            print(f"  Need   {row(acc, self.need[i])}")
            if i < self.n - 1:
                print(f"  {'·'*len(sep)}")
        print()


# ── System Setup ───────────────────────────────────────────────────────────

def create_demo_system():
    """
    5 accounts (A001–A005), 3 fund types:
      FX   = Foreign Exchange reserves
      BOND = Bond collateral
      CASH = Liquid cash pool
    Units are in $1,000.
    """
    accounts   = ["A001", "A002", "A003", "A004", "A005"]
    fund_types = ["FX  ", "BOND", "CASH"]
    total      = [10, 14, 12]

    #            FX  BOND CASH
    allocation = [
        [0, 1, 0],   # A001
        [2, 0, 0],   # A002
        [3, 0, 2],   # A003
        [2, 1, 1],   # A004
        [0, 0, 2],   # A005
    ]

    #           FX  BOND CASH
    max_need = [
        [7, 5, 3],   # A001
        [3, 2, 2],   # A002
        [9, 0, 2],   # A003
        [2, 2, 2],   # A004
        [4, 3, 3],   # A005
    ]

    return BankersAlgorithm(accounts, fund_types, total, allocation, max_need)


TRANSFER_REQUESTS = [
    # (account, [FX, BOND, CASH], label)
    ("A001", [0, 1, 0], "Routine FX top-up"),
    ("A002", [1, 0, 2], "Bond + cash increase"),   # should be safe
    ("A003", [3, 0, 0], "Large FX grab"),           # might be unsafe
    ("A004", [0, 0, 1], "Small cash request"),
    ("A005", [2, 1, 1], "Mixed resource request"),
    ("A001", [4, 0, 1], "Big FX — exceeds need"),   # exceeds max need
    ("A003", [0, 0, 1], "Cash after big grab"),
]


def run_bankers_demo():
    print("\n" + "█"*60)
    print("  BANKER'S ALGORITHM — Deadlock Prevention")
    print("█"*60)

    banker = create_demo_system()
    banker.print_state()

    safe, seq = banker.is_safe(verbose=True)
    status = "SAFE ✓" if safe else "UNSAFE ✗"
    print(f"\n  Initial state: {status}")
    if safe:
        print(f"  Safe sequence: {' → '.join(seq)}")

    print(f"\n\n{'━'*60}")
    print("  Processing Transfer Requests")
    print("━"*60)

    results = []
    for account, req, label in TRANSFER_REQUESTS:
        print(f"\n  [{label}]")
        result = banker.request_resources(account, req, verbose=True)
        results.append((label, result))

    return results


if __name__ == "__main__":
    run_bankers_demo()