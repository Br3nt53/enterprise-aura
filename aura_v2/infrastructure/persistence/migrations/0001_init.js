// Creates base collections and time indexes (non-TTL)
function run(db) {
  const collections = ["tracks", "detections", "metrics", "audit"];
  collections.forEach(c => {
    if (!db.getCollectionNames().includes(c)) db.createCollection(c);
    db[c].createIndex({ ts: 1 }, { name: "ts_idx", background: true });
  });
}
// Usage: mongosh <db> 0001_init.js
