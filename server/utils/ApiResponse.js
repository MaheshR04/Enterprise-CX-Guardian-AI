/**
 * Standard Success Response class template matching unified API response schema.
 */
class ApiResponse {
  constructor(statusCode, data, message = 'Success') {
    this.success = statusCode < 400;
    this.message = message;
    this.data = data || null;
    this.errors = null;
  }
}

export default ApiResponse;
