// Adds TTL indexes using environment-provided seconds (supply via driver in code for dynamic)
function run(db, expiries) {
  // expiries example: { tracks: 604800, detections: 259200, metrics: 1209600, audit: 2592000 }
  Object.entries(expiries).forEach(([coll, seconds]) => {
    db[coll].createIndex({ ts: 1 }, { expireAfterSeconds: seconds, name: `ttl_ts_${seconds}`, background: true });
  });
}
// Prefer programmatic creation from app for consistency with env.
