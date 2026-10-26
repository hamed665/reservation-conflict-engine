# SlotGuard

**Transactional, timezone-aware booking with resource conflict detection.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB)
![License](https://img.shields.io/badge/license-MIT-green)

Prevent two requests from reserving the same resource, even when they arrive through different connections.

An original, runnable reference implementation by Hamed Minaei. Uses only the
Python standard library. No API key, paid account or network access is needed
for the included demos and tests. Version 0.1.0 focuses on the core engineering
contract rather than a hosted production service.

## Capabilities

- Offset-aware timestamps normalized to UTC seconds
- Half-open intervals allow adjacent appointments
- Tenant-scoped idempotency keys with payload mismatch rejection
- BEGIN IMMEDIATE serializes overlap checks and insertion
- Cancellation releases capacity without deleting audit rows

## Quick start

```bash
git clone https://github.com/hamed665/reservation-conflict-engine.git
cd reservation-conflict-engine
python --version  # Python 3.11+
python -m slotguard
python -m unittest discover -s tests -v
```

Optional library installation: `python -m pip install .`

## Use as a library

```python
from slotguard.core import Calendar
c = Calendar("calendar.db")
c.book("demo", "booking-1", "room-1", "2026-11-01T10:00:00+04:00", "2026-11-01T10:30:00+04:00")
c.close()
```

## Data flow

Caller → UTC validation → SQLite write transaction → conflict query → booking

See [slotguard/core.py](slotguard/core.py) for the implementation and [architecture notes](docs/architecture.md)
for transaction boundaries and deployment considerations.

## Verification

The test suite exercises behavioral guarantees, error paths and isolation.
SQLite projects also test competing connections with independent workers.
GitHub Actions runs the suite on Python 3.11, 3.12 and 3.13.
All fixtures are synthetic. Demo output is captured in
[examples/demo-output.txt](examples/demo-output.txt).

## Scope and limitations

Each booking reserves one resource. There are no recurrence rules, capacity pools, reminders, UI or external calendar connectors. Clients must resolve ambiguous local times to explicit offsets before calling. Tenant IDs are namespaces, not authentication. Cancelled identifiers cannot be reused.

## Repository map

- `slotguard/`: importable library and runnable CLI demo
- `tests/`: regression and invariant tests
- `examples/`: synthetic inputs and captured demo output
- `docs/`: design decisions and boundaries
- `.github/workflows/ci.yml`: repeatable verification

## License

MIT. See [LICENSE](LICENSE). Contributions: [CONTRIBUTING.md](CONTRIBUTING.md).
