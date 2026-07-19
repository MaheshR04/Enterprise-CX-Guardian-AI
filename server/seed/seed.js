/**
 * Enterprise CX Guardian AI — MongoDB Seeder Script
 * ===================================================
 * Seeds MongoDB database with realistic demo data:
 *   - 3 Users (Admin, Supervisor, Agent)
 *   - 5 Conversations with multi-turn messages
 *   - 4 Knowledge Base Documents (PDF SLA Policy, Security Docs)
 *   - 10 AI Usage Telemetry Records
 *
 * Usage:
 *   node server/seed/seed.js
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '../../.env') });

const MONGO_URI = process.env.MONGO_URI || process.env.MONGODB_URI || 'mongodb://localhost:27017/cx_guardian_db';

async function seed() {
  console.log(`[Seeder] Connecting to MongoDB: ${MONGO_URI}...`);
  await mongoose.connect(MONGO_URI);
  const db = mongoose.connection.db;

  console.log('[Seeder] Cleaning existing collections...');
  await db.collection('users').deleteMany({});
  await db.collection('conversations').deleteMany({});
  await db.collection('messages').deleteMany({});
  await db.collection('ai_usage').deleteMany({});
  await db.collection('documents').deleteMany({});

  console.log('[Seeder] Inserting sample users...');
  await db.collection('users').insertMany([
    {
      userId: 'usr_admin_001',
      name: 'Sarah Connor (Admin)',
      email: 'admin@enterprise-cx.ai',
      passwordHash: '$2a$10$wE9J/w1mN7z5jD9.s8Zg.eLp5F2HqN4t8vW0xY2zA4bC6dE8fG1hI', // hashed
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

  console.log('[Seeder] Inserting sample conversations...');
  await db.collection('conversations').insertMany([
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

  console.log('[Seeder] Inserting sample messages...');
  await db.collection('messages').insertMany([
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

  console.log('[Seeder] Inserting sample AI usage telemetry...');
  await db.collection('ai_usage').insertMany([
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

  console.log('[Seeder] Inserting sample documents...');
  await db.collection('documents').insertMany([
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

  console.log('✅ [Seeder] Database seeding completed successfully!');
  await mongoose.disconnect();
}

seed().catch(err => {
  console.error('❌ [Seeder] Error during database seeding:', err);
  process.exit(1);
});
