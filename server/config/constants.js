/**
 * System-wide constants for Enterprise CX Guardian AI
 */
export const TICKET_STATUS = {
  OPEN: 'Open',
  PENDING: 'Pending',
  RESOLVED: 'Resolved',
  ESCALATED: 'Escalated',
  CRITICAL: 'Critical'
};

export const TICKET_PRIORITY = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  URGENT: 'Urgent'
};

export const USER_ROLES = {
  ADMIN: 'Admin',
  AGENT: 'Agent',
  CUSTOMER: 'Customer'
};

export const SLA_THRESHOLDS = {
  STANDARD: 24, // hours
  GOLD: 2,       // hours
  PLATINUM: 1    // hour
};

export const REFUND_LIMITS = {
  AUTO_MAX: 500, // USD maximum auto-refund limit
};
