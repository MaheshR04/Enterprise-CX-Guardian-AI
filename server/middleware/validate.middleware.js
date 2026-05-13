import { createError } from '../utils/appError.js';

export function validate(schema) {
  return (req, _res, next) => {
    const result = schema.safeParse(req.body);

    if (!result.success) {
      const message = result.error.issues.map((issue) => issue.message).join(', ');
      return next(createError(message, 400));
    }

    req.body = result.data;
    return next();
  };
}
