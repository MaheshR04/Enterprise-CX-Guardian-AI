import asyncHandler from '../utils/asyncHandler.js';

/**
 * @desc Login user credentials
 * @route POST /api/v1/auth/login
 */
export const login = asyncHandler(async (req, res, next) => {
  res.ok({}, "Auth Login API Working - Controller Active");
});

/**
 * @desc Register user details
 * @route POST /api/v1/auth/register
 */
export const register = asyncHandler(async (req, res, next) => {
  res.created({}, "Auth Register API Working - Controller Active");
});
