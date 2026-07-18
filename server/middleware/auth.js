import { JWT_SECRET } from '../config/index.js';

/**
 * Reusable Authentication Guard template.
 * Do NOT implement JWT logic yet (stub placeholder).
 */
export const protect = async (req, res, next) => {
  let token;

  // Check for authorization header Bearer token
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }

  if (!token) {
    return res.status(401).json({
      success: false,
      message: 'Not authorized, token credentials are required'
    });
  }

  try {
    // TODO: Verify JWT token payload using jsonwebtoken library:
    // const decoded = jwt.verify(token, JWT_SECRET);
    // req.user = await User.findById(decoded.id).select('-password');
    
    // Stub validation mapping a mock user payload for routing checks
    req.user = {
      id: 'usr_mock_9910a',
      role: 'Admin',
      email: 'guardian@company.com'
    };

    next();
  } catch (error) {
    res.status(401).json({
      success: false,
      message: 'Not authorized, token credentials invalid'
    });
  }
};

/**
 * Restricts access to specific roles (e.g., Admin, Agent).
 */
export const authorizeRoles = (...roles) => {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: `Role (${req.user ? req.user.role : 'Guest'}) is not allowed to access this resource`
      });
    }
    next();
  };
};
