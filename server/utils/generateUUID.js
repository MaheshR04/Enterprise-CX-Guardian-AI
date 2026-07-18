import crypto from 'crypto';

/**
 * Generate cryptographically secure UUID v4 strings.
 */
const generateUUID = () => {
  return crypto.randomUUID();
};

export default generateUUID;
