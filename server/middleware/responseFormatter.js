/**
 * Middleware binding helpers for standardized success response formats.
 */
const responseFormatter = (req, res, next) => {
  
  // 200 OK success reply
  res.ok = (data = {}, message = 'Success') => {
    res.status(200).json({
      success: true,
      message,
      data,
      errors: null
    });
  };

  // 201 Created success reply
  res.created = (data = {}, message = 'Resource Created Successfully') => {
    res.status(201).json({
      success: true,
      message,
      data,
      errors: null
    });
  };

  next();
};

export default responseFormatter;
