import jwt from 'jsonwebtoken';
import { env } from '../config/env.js';

export function signToken(userId) {
  if (!env.JWT_SECRET) {
    throw new Error('JWT_SECRET is required to sign authentication tokens');
  }

  return jwt.sign({ userId }, env.JWT_SECRET, {
    expiresIn: env.JWT_EXPIRES_IN,
  });
}

export function verifyToken(token) {
  if (!env.JWT_SECRET) {
    throw new Error('JWT_SECRET is required to verify authentication tokens');
  }

  return jwt.verify(token, env.JWT_SECRET);
}
