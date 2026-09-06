"""
Main Driver — Transaction Management System
Runs all three modules in sequence:
  1. Greedy Activity Selection (Transaction Scheduling)
  2. Banker's Algorithm        (Deadlock Prevention)
  3. Deadlock Detection        (Bonus — Circular Wait Finder)
"""

import sys
from activity_selection import run_activity_selection_demo
from bankers_algorithm   import run_bankers_demo, create_demo_system, TRANSFER_REQUESTS
from deadlock_detection  import run_detection_demo


def print_banner():
    print("\n" + "▓"*60)
    print("▓" + " "*58 + "▓")
    print("▓   DIGITAL BANK — TRANSACTION MANAGEMENT SYSTEM        ▓")
    print("▓   DAA: Greedy Activity Selection                       ▓")
    print("▓   OS : Banker's Algorithm + Deadlock Detection         ▓")
    print("▓" + " "*58 + "▓")
    print("▓"*60)


def print_section(title, number):
    print(f"\n\n{'#'*60}")
    print(f"#  MODULE {number}: {title}")
    print(f"{'#'*60}")


def demo_deadlock_prevention_scenario():
    """
    Specific scenario showing Banker's rejection preventing a deadlock.
    """
    print(f"\n{'━'*60}")
    print("  DEADLOCK PREVENTION SCENARIO")
    print("━"*60)
    print("""
  Setup:
  - 5 accounts (A001–A005) share 3 fund pools: FX, BOND, CASH
  - Each account has a declared maximum need
  - The system approves requests only if the resulting state is SAFE

  Scenario — Dangerous Request Sequence:
  Step 1: A003 requests [3,0,0] (large FX grab)
          → Banker checks: would this leave enough for all others?
          → If unsafe: REJECTED, rollback, suggest smaller amount
  Step 2: After rejection, A003 tries a reduced request
          → Banker approves if safe sequence exists
    """)

    banker = create_demo_system()

    print("  [Step 1] A003 tries to grab 3 FX units ...")
    r1 = banker.request_resources("A003", [3, 0, 0], verbose=True)

    if not r1["approved"]:
        print("\n  [Step 2] A003 follows the suggestion ...")
        suggestion = r1.get("suggestion")
        if suggestion:
            r2 = banker.request_resources("A003", suggestion, verbose=True)
            if r2["approved"]:
                print("\n  ✓ Deadlock prevented. System remains in safe state.")
        else:
            print("  No safe alternative found for A003 at this time.")
    else:
        print("\n  ✓ Request was safe to approve directly.")


def print_summary(bankers_results):
    approved = sum(1 for _, r in bankers_results if r["approved"])
    rejected = len(bankers_results) - approved

    print(f"\n\n{'═'*60}")
    print("  FINAL SUMMARY")
    print(f"{'═'*60}")
    print(f"\n  Banker's Algorithm Results:")
    print(f"    Total requests  : {len(bankers_results)}")
    print(f"    Approved        : {approved}  ✓")
    print(f"    Rejected        : {rejected}  ✗")
    print(f"\n  Request Breakdown:")
    for label, result in bankers_results:
        status = "✓ APPROVED" if result["approved"] else "✗ REJECTED"
        print(f"    [{status}]  {label}")
    print()


def main():
    print_banner()

    # ── Module 1 ──────────────────────────────────────────────────────────
    print_section("GREEDY ACTIVITY SELECTION", 1)
    run_activity_selection_demo()

    # ── Module 2 ──────────────────────────────────────────────────────────
    print_section("BANKER'S ALGORITHM (DEADLOCK PREVENTION)", 2)
    bankers_results = run_bankers_demo()

    # ── Scenario Demo ─────────────────────────────────────────────────────
    print_section("DEADLOCK PREVENTION SCENARIO", 3)
    demo_deadlock_prevention_scenario()

    # ── Module 3 (Bonus) ──────────────────────────────────────────────────
    print_section("BONUS — DEADLOCK DETECTION & CIRCULAR WAIT", 4)
    run_detection_demo()

    # ── Summary ───────────────────────────────────────────────────────────
    print_summary(bankers_results)

    print("  All modules completed successfully.")
    print("═"*60 + "\n")


if __name__ == "__main__":
    main()