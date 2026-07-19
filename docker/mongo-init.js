// docker/mongo-init.js
// MongoDB initialization script — runs once when the container is first created.
// Creates application DB user with read/write access.

db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE || 'cx_guardian_db');

db.createUser({
  user: 'cx_app_user',
  pwd:  process.env.MONGO_ROOT_PASSWORD || 'secret',
  roles: [{ role: 'readWrite', db: process.env.MONGO_INITDB_DATABASE || 'cx_guardian_db' }]
});

// Create indexes for the main collections
db.conversations.createIndex({ conversation_id: 1 }, { unique: true });
db.conversations.createIndex({ status: 1 });
db.conversations.createIndex({ created_at: -1 });

db.messages.createIndex({ conversation_id: 1, timestamp: 1 });
db.messages.createIndex({ message_id: 1 }, { unique: true });

db.prompt_logs.createIndex({ conversation_id: 1, created_at: -1 });
db.ai_usage.createIndex({ conversation_id: 1, timestamp: -1 });

db.users.createIndex({ email: 1 }, { unique: true });
db.refresh_tokens.createIndex({ token: 1 }, { unique: true });
db.refresh_tokens.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 }); // TTL index

print('[mongo-init] Database and indexes initialized successfully.');
