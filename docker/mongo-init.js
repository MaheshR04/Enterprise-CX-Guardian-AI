// docker/mongo-init.js
// MongoDB initialization script — runs once when the container is first created.
// Creates application DB user with read/write access and seeds realistic demo data.

db = db.getSiblingDB(process.env.MONGO_INITDB_DATABASE || 'cx_guardian_db');

db.createUser({
  user: 'cx_app_user',
  pwd:  process.env.MONGO_ROOT_PASSWORD || 'secret',
  roles: [{ role: 'readWrite', db: process.env.MONGO_INITDB_DATABASE || 'cx_guardian_db' }]
});

// ── Create Indexes ────────────────────────────────────────────────
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

// ── Seed Demo Data ────────────────────────────────────────────────

// 1. Users
db.users.insertMany([
  {
    userId: 'usr_admin_001',
    name: 'Sarah Connor (Admin)',
    email: 'admin@enterprise-cx.ai',
    passwordHash: '$2a$10$wE9J/w1mN7z5jD9.s8Zg.eLp5F2HqN4t8vW0xY2zA4bC6dE8fG1hI',
    role: 'ADMIN',
    status: 'ACTIVE',
    createdAt: new Date().toISOString()
  },
  {
    userId: 'usr_supervisor_002',
    name: 'Marcus Wright (Supervisor)',
    email: 'supervisor@enterprise-cx.ai',
    passwordHash: '$2a$10$wE9J/w1mN7z5jD9.s8Zg.eLp5F2HqN4t8vW0xY2zA4bC6dE8fG1hI',
    role: 'SUPERVISOR',
    status: 'ACTIVE',
    createdAt: new Date().toISOString()
  },
  {
    userId: 'usr_agent_003',
    name: 'John Reese (Agent)',
    email: 'agent@enterprise-cx.ai',
    passwordHash: '$2a$10$wE9J/w1mN7z5jD9.s8Zg.eLp5F2HqN4t8vW0xY2zA4bC6dE8fG1hI',
    role: 'AGENT',
    status: 'ACTIVE',
    createdAt: new Date().toISOString()
  }
]);

// 2. Conversations
db.conversations.insertMany([
  {
    conversation_id: 'conv_demo_enterprise_sla',
    status: 'ACTIVE',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date().toISOString(),
    metadata: { customer_tier: 'Enterprise Gold', subject: 'Downtime Credit Request' }
  },
  {
    conversation_id: 'conv_demo_security_audit',
    status: 'ACTIVE',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    updated_at: new Date().toISOString(),
    metadata: { customer_tier: 'Platinum', subject: 'SOC2 Compliance Audit' }
  },
  {
    conversation_id: 'conv_demo_billing_inquiry',
    status: 'ARCHIVED',
    created_at: new Date(Date.now() - 86400000).toISOString(),
    updated_at: new Date().toISOString(),
    metadata: { customer_tier: 'Silver', subject: 'Invoice Discrepancy' }
  }
]);

// 3. Messages
db.messages.insertMany([
  {
    message_id: 'msg_001',
    conversation_id: 'conv_demo_enterprise_sla',
    sender: 'user',
    text: 'Our API endpoint experienced 45 minutes of downtime today. Are we eligible for SLA credit compensation?',
    timestamp: new Date(Date.now() - 3500000).toISOString()
  },
  {
    message_id: 'msg_002',
    conversation_id: 'conv_demo_enterprise_sla',
    sender: 'assistant',
    text: 'According to Section 4.2 of your Enterprise Gold SLA agreement, service outages exceeding 30 minutes qualify for a 15% monthly bill credit. I have initiated Ticket #CX-4912 for service credit authorization.',
    timestamp: new Date(Date.now() - 3400000).toISOString()
  }
]);

// 4. AI Usage Telemetry
db.ai_usage.insertMany([
  {
    usage_id: 'usg_001',
    conversation_id: 'conv_demo_enterprise_sla',
    model: 'llama3-70b-8192',
    prompt_tokens: 48,
    completion_tokens: 64,
    total_tokens: 112,
    latency_ms: 42.5,
    timestamp: new Date().toISOString()
  }
]);

// 5. Knowledge Documents
db.documents.insertMany([
  {
    document_id: 'doc_sla_policy_2026',
    title: 'Enterprise SLA & Service Guarantee Policy 2026.pdf',
    chunks: 42,
    category: 'SLA',
    uploaded_at: new Date().toISOString()
  },
  {
    document_id: 'doc_sec_soc2_report',
    title: 'SOC2 Type II Compliance Report 2026.pdf',
    chunks: 128,
    category: 'Compliance',
    uploaded_at: new Date().toISOString()
  }
]);

print('[mongo-init] Database, indexes, and demo data initialized successfully.');
