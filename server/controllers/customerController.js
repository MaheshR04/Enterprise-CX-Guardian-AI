import asyncHandler from '../utils/asyncHandler.js';
import customerService from '../services/customer.service.js';

/**
 * @desc Get all customers
 * @route GET /api/v1/customers
 */
export const getCustomers = asyncHandler(async (req, res, next) => {
  const customers = await customerService.getCustomers();
  res.ok(customers, "Customer API Working - Controller Active");
});

/**
 * @desc Get single customer by id
 * @route GET /api/v1/customers/:id
 */
export const getCustomerById = asyncHandler(async (req, res, next) => {
  const customer = await customerService.getCustomerById(req.params.id);
  res.ok(customer, `Customer details for id ${req.params.id} Working - Controller Active`);
});
