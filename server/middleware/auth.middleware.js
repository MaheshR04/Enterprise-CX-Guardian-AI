import User from '../models/User.model.js';
import { createError } from '../utils/appError.js';
import { asyncHandler } from '../utils/asyncHandler.js';
import { verifyToken } from '../utils/jwt.js';

export const protect = asyncHandler(async (req, _res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader?.startsWith('Bearer ') ? authHeader.split(' ')[1] : null;

  if (!token) {
    throw createError('Authentication token is required', 401);
  }

  let decoded;

  try {
    decoded = verifyToken(token);
  } catch {
    throw createError('Invalid or expired authentication token', 401);
  }

  const user = await User.findById(decoded.userId);

  if (!user) {
    throw createError('User no longer exists', 401);
  }

  req.user = user;
  next();
});
