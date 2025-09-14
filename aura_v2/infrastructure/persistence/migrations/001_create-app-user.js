// Creates an application-scoped user on first boot
const dbName = process.env.MONGO_DB || "aura_test";
const user = process.env.MONGO_USER || "admin";
const pwd = process.env.MONGO_PASSWORD || "secret";

const db = db.getSiblingDB(dbName);
db.createUser({
  user: user,
  pwd: pwd,
  roles: [{ role: "readWrite", db: dbName }]
});
print(`Created app user '${user}' on db '${dbName}'`);
