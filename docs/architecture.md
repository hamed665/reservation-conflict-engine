# Design notes — SlotGuard

## Contract

Prevent two requests from reserving the same resource, even when they arrive through different connections.

## Execution path

Caller → UTC validation → SQLite write transaction → conflict query → booking

## Design choices

1. Offset-aware timestamps normalized to UTC seconds.
2. Half-open intervals allow adjacent appointments.
3. Tenant-scoped idempotency keys with payload mismatch rejection.
4. BEGIN IMMEDIATE serializes overlap checks and insertion.
5. Cancellation releases capacity without deleting audit rows.

## Integration boundary

Each booking reserves one resource. There are no recurrence rules, capacity pools, reminders, UI or external calendar connectors. Clients must resolve ambiguous local times to explicit offsets before calling. Tenant IDs are namespaces, not authentication. Cancelled identifiers cannot be reused.

## Failure handling

Validation errors are explicit exceptions. SQLite mutations use bound SQL
parameters; multi-step mutations commit together or roll back. Library results
are data structures suitable for an adapter layer. No network calls or secrets
are embedded in the examples.

## Before deployment

Choose an authenticated adapter, add structured operational logging without raw
customer data, define backup and retention requirements, and test realistic
workloads. The local tests establish specific invariants; they do not establish
production throughput, external integration compatibility or service availability.
