import { validationResult } from 'express-validator';

/**
 * Reusable middleware to inspect validation results and return unified error formats.
 */
const validateFields = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const errorDetails = errors.array().map(err => `${err.path}: ${err.msg}`).join(', ');
    return res.status(400).json({
      success: false,
      message: 'Validation Error',
      error: errorDetails,
      stack: undefined
    });
  }
  next();
};

export default validateFields;
