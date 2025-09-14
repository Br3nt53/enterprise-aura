# Migrations

Lightweight migration tracking for Mongo.

A collection `_migrations` will store:
```json
{ "_id": "<migration_id>", "applied_at": "<timestamp>" }
```

Run all unapplied migrations at startup:
1. Discover files `000*_*.py`
2. Sort lexicographically
3. Skip if `_id` present
4. Execute `upgrade(db)`
5. Insert record

Add new migration:
- Copy template
- Increment numeric prefix

Rollback strategy intentionally omitted (append-only evolution).
