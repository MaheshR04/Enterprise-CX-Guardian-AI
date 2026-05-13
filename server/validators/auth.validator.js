import { z } from 'zod';

const phoneSchema = z
  .string()
  .trim()
  .min(7, 'Phone number must be at least 7 characters')
  .max(20, 'Phone number must be at most 20 characters');

export const guardianContactSchema = z.object({
  name: z.string().trim().min(2, 'Guardian name is required').max(80),
  phoneNumber: phoneSchema,
  relationship: z.string().trim().max(50).optional().default('Guardian'),
});

export const signupSchema = z.object({
  name: z.string().trim().min(2, 'Name must be at least 2 characters').max(80),
  email: z.email('Please enter a valid email').toLowerCase(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  phoneNumber: phoneSchema,
  guardianContacts: z.array(guardianContactSchema).max(5).optional().default([]),
});

export const loginSchema = z.object({
  email: z.email('Please enter a valid email').toLowerCase(),
  password: z.string().min(1, 'Password is required'),
});

export const guardianContactsSchema = z.object({
  guardianContacts: z.array(guardianContactSchema).max(5, 'You can save up to 5 guardian contacts'),
});
