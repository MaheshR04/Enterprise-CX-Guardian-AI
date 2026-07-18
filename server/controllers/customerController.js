import asyncHandler from '../utils/asyncHandler.js';

/**
 * @desc Get all customers
 * @route GET /api/v1/customers
 */
export const getCustomers = asyncHandler(async (req, res, next) => {
  res.ok([], "Customer API Working - Controller Active");
});

/**
 * @desc Get single customer by id
 * @route GET /api/v1/customers/:id
 */
export const getCustomerById = asyncHandler(async (req, res, next) => {
  res.ok({}, `Customer details for id ${req.params.id} Working - Controller Active`);
});
