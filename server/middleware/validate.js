/**
 * Reusable schema validation middleware template.
 * Integrates Joi or custom validators schemas mapping body, query, or params.
 */
const validate = (schema, source = 'body') => {
  return (req, res, next) => {
    // Check if validator functions or schema checks exist
    if (!schema) {
      return next();
    }

    try {
      // Stub check: Joi validation syntax template
      // const { error } = schema.validate(req[source]);
      // if (error) throw new Error(error.details[0].message);
      
      next();
    } catch (err) {
      res.status(400).json({
        success: false,
        message: err.message || 'Validation error'
      });
    }
  };
};

export default validate;
