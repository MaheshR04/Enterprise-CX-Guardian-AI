import User from '../models/User.model.js';
import { createError } from '../utils/appError.js';
import { asyncHandler } from '../utils/asyncHandler.js';
import { signToken } from '../utils/jwt.js';

function sendAuthResponse(res, statusCode, user) {
  const token = signToken(user._id);

  res.status(statusCode).json({
    success: true,
    token,
    user,
  });
}

export const signup = asyncHandler(async (req, res) => {
  const existingUser = await User.findOne({ email: req.body.email });

  if (existingUser) {
    throw createError('An account with this email already exists', 409);
  }

  const user = await User.create(req.body);

  sendAuthResponse(res, 201, user);
});

export const login = asyncHandler(async (req, res) => {
  const user = await User.findOne({ email: req.body.email }).select('+password');

  if (!user || !(await user.comparePassword(req.body.password))) {
    throw createError('Invalid email or password', 401);
  }

  user.password = undefined;
  sendAuthResponse(res, 200, user);
});

export const getMe = asyncHandler(async (req, res) => {
  res.status(200).json({
    success: true,
    user: req.user,
  });
});

export const updateGuardianContacts = asyncHandler(async (req, res) => {
  req.user.guardianContacts = req.body.guardianContacts;
  await req.user.save();

  res.status(200).json({
    success: true,
    user: req.user,
  });
});

export function logout(_req, res) {
  res.status(200).json({
    success: true,
    message: 'Logged out successfully',
  });
}
