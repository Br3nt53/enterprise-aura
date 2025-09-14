# Mongo Retention Runbook

## Migrations
- `mongosh <db> aura_v2/infrastructure/persistence/migrations/0001_init.js`
- TTLs are created by the app at startup from env hours.

## Backups
- Use `mongodump --db "$MONGO_DB" --out backups/$(date -u +%FT%TZ)`

## Restore
- `mongorestore --db "$MONGO_DB" backups/<stamp>`

## Verification
- `db.tracks.getIndexes()`
- Ensure index `ttl_ts_*` exists on `tracks`, `detections`, `metrics`, `audit`.
