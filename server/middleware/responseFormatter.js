/**
 * Middleware binding helpers for standardized success response formats.
 */
const responseFormatter = (req, res, next) => {
  
  // 200 OK success reply
  res.ok = (data = {}, message = 'Request completed successfully') => {
    return res.status(200).json({
      success: true,
      message,
      data: data !== undefined ? data : {}
    });
  };

  // 201 Created success reply
  res.created = (data = {}, message = 'Resource Created Successfully') => {
    return res.status(201).json({
      success: true,
      message,
      data: data !== undefined ? data : {}
    });
  };

  next();
};

export default responseFormatter;
