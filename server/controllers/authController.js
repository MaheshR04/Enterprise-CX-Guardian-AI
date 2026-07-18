import asyncHandler from '../utils/asyncHandler.js';
import authService from '../services/auth.service.js';

/**
 * @desc Login user credentials
 * @route POST /api/v1/auth/login
 */
export const login = asyncHandler(async (req, res, next) => {
  const result = await authService.login(req.body);
  res.ok(result, "Auth Login API Working - Controller Active");
});

/**
 * @desc Register user details
 * @route POST /api/v1/auth/register
 */
export const register = asyncHandler(async (req, res, next) => {
  const result = await authService.register(req.body);
  res.created(result, "Auth Register API Working - Controller Active");
});
