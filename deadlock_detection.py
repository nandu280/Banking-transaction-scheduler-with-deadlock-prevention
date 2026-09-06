"""
Deadlock Detection (Bonus)
Given a resource-allocation graph or wait-for graph,
detect circular wait chains using DFS cycle detection.
"""

from collections import defaultdict


class DeadlockDetector:
    """
    Builds a Wait-For Graph (WFG) from a deadlocked state.
    Account A 'waits for' Account B if A needs resources that B holds.
    Cycles in the WFG = deadlocks.
    """

    def __init__(self, accounts, fund_types, allocation, need, available):
        self.accounts   = accounts
        self.fund_types = fund_types
        self.n          = len(accounts)
        self.m          = len(fund_types)
        self.allocation = allocation
        self.need       = need
        self.available  = available
        self.wfg        = defaultdict(set)   # wait-for graph

    def _can_satisfy(self, need_row, work):
        return all(need_row[j] <= work[j] for j in range(self.m))

    # ── Resource-Allocation Graph → Wait-For Graph ─────────────────────────

    def build_wait_for_graph(self):
        """
        Account i waits for account j if:
          - i cannot be satisfied with current available resources, AND
          - j holds at least one resource type that i needs.
        """
        self.wfg.clear()

        # Which accounts are blocked (cannot proceed)?
        work   = self.available[:]
        finish = [False] * self.n

        # First pass: mark who CAN run immediately
        for i in range(self.n):
            if self._can_satisfy(self.need[i], work):
                finish[i] = True

        # Blocked accounts wait for holders of their needed resources
        for i in range(self.n):
            if finish[i]:
                continue
            for j in range(self.n):
                if i == j:
                    continue
                # Does j hold anything that i needs?
                for r in range(self.m):
                    if self.need[i][r] > 0 and self.allocation[j][r] > 0:
                        self.wfg[self.accounts[i]].add(self.accounts[j])
                        break

        return dict(self.wfg)

    # ── Cycle Detection (DFS) ──────────────────────────────────────────────

    def find_cycles(self):
        """Find all simple cycles in the wait-for graph using DFS."""
        visited = set()
        rec_stack = []
        cycles = []

        def dfs(node, path):
            visited.add(node)
            rec_stack.append(node)
            for neighbour in self.wfg.get(node, []):
                if neighbour not in visited:
                    dfs(neighbour, path + [neighbour])
                elif neighbour in rec_stack:
                    # Found a cycle — extract it
                    cycle_start = rec_stack.index(neighbour)
                    cycle = rec_stack[cycle_start:]
                    cycles.append(list(cycle))
            rec_stack.pop()

        all_nodes = set(self.wfg.keys())
        for node in all_nodes:
            if node not in visited:
                dfs(node, [node])

        # Deduplicate cycles (same cycle, different starting point)
        unique = []
        seen_sets = []
        for c in cycles:
            s = frozenset(c)
            if s not in seen_sets:
                unique.append(c)
                seen_sets.append(s)
        return unique

    # ── Resource-Allocation Algorithm check ───────────────────────────────

    def detection_algorithm(self, verbose=True):
        """
        Classic OS deadlock detection:
        Similar to Banker's safety check but without max_need assumption.
        Returns list of deadlocked accounts.
        """
        work   = self.available[:]
        finish = [None] * self.n   # None = not yet processed

        # Mark processes with zero allocation as finished (not involved)
        for i in range(self.n):
            if all(self.allocation[i][j] == 0 for j in range(self.m)):
                finish[i] = True

        changed = True
        while changed:
            changed = False
            for i in range(self.n):
                if finish[i] is not None:
                    continue
                if self._can_satisfy(self.need[i], work):
                    for j in range(self.m):
                        work[j] += self.allocation[i][j]
                    finish[i] = True
                    changed = True

        deadlocked = [
            self.accounts[i]
            for i in range(self.n)
            if finish[i] is None
        ]

        if verbose:
            print(f"\n{'='*60}")
            print("  DEADLOCK DETECTION ALGORITHM")
            print(f"{'='*60}")
            if deadlocked:
                print(f"\n  ⚠  DEADLOCK DETECTED among: {', '.join(deadlocked)}")
            else:
                print("\n  ✓  No deadlock detected — all accounts can complete.")

        return deadlocked

    # ── Full Analysis ──────────────────────────────────────────────────────

    def full_analysis(self):
        print(f"\n{'='*60}")
        print("  DEADLOCK DETECTION — Full Analysis")
        print(f"{'='*60}")

        # Step 1: Detection algorithm
        deadlocked = self.detection_algorithm(verbose=True)

        # Step 2: Build & display WFG
        wfg = self.build_wait_for_graph()
        print(f"\n  Wait-For Graph:")
        if wfg:
            for acc, waiting_for in sorted(wfg.items()):
                print(f"    {acc}  →  {', '.join(sorted(waiting_for))}")
        else:
            print("    (empty — no waits)")

        # Step 3: Find cycles
        cycles = self.find_cycles()
        print(f"\n  Circular Wait Chains:")
        if cycles:
            for i, cycle in enumerate(cycles, 1):
                chain = " → ".join(cycle) + f" → {cycle[0]}"
                print(f"    Cycle {i}: {chain}")
                print(f"    Accounts involved: {', '.join(cycle)}")
        else:
            print("    None detected.")

        # Step 4: Recovery suggestion
        if deadlocked:
            print(f"\n  Recovery Suggestion:")
            print(f"    Preempt resources from: {deadlocked[0]}")
            print(f"    (Rollback {deadlocked[0]}'s allocation and redistribute)")

        return {"deadlocked": deadlocked, "cycles": cycles, "wfg": wfg}


# ── Demo: Manually create a deadlocked state ──────────────────────────────

def create_deadlocked_state():
    """
    Construct a state that IS already deadlocked so detection can find it.
    4 accounts, 2 resource types.
    Circular wait: A001 → A002 → A003 → A001
    """
    accounts   = ["A001", "A002", "A003", "A004"]
    fund_types = ["FX  ", "CASH"]

    #            FX  CASH
    allocation = [
        [1, 0],  # A001 holds 1 FX
        [0, 1],  # A002 holds 1 CASH
        [1, 0],  # A003 holds 1 FX
        [0, 0],  # A004 holds nothing
    ]

    # Still need (can't proceed):
    #              FX  CASH
    need = [
        [0, 1],  # A001 needs CASH (held by A002)
        [1, 0],  # A002 needs FX   (held by A003)
        [0, 1],  # A003 needs CASH (held by A002) — cycle!
        [0, 0],  # A004 needs nothing — not involved
    ]

    available = [0, 0]  # Nothing freely available → deadlock certain

    return DeadlockDetector(accounts, fund_types, allocation, need, available)


def run_detection_demo():
    print("\n" + "█"*60)
    print("  BONUS: DEADLOCK DETECTION")
    print("█"*60)

    print("\n  Scenario: 3 accounts in circular wait, 1 free account.")
    print("  A001 holds FX, needs CASH")
    print("  A002 holds CASH, needs FX")
    print("  A003 holds FX, needs CASH  ← forms cycle with A002")
    print("  A004 has nothing, needs nothing  ← not involved")

    detector = create_deadlocked_state()
    result = detector.full_analysis()
    return result


if __name__ == "__main__":
    run_detection_demo()