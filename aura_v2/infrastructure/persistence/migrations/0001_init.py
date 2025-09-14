from datetime import datetime

MIGRATION_ID = "0001_init"


def upgrade(db):
    db.tracks.create_index("updated_at")
    db.tracks.create_index([("x", 1), ("y", 1)])
    db._migrations.insert_one({"_id": MIGRATION_ID, "applied_at": datetime.utcnow()})
