import asyncHandler from '../utils/asyncHandler.js';
import ApiError from '../utils/ApiError.js';
import aiService from '../services/ai.service.js';

/**
 * @desc Process chat message and receive AI response
 * @route POST /api/v1/chat
 * @access Public / Authenticated
 */
export const sendChatMessage = asyncHandler(async (req, res, next) => {
  const { message, conversationId, conversation_id, customerId, customer_id } = req.body;

  // 1. Input Validation Fallback Check
  if (!message || typeof message !== 'string' || !message.trim()) {
    throw new ApiError(400, 'Message content is required and cannot be empty.');
  }

  const selectedConversationId = conversationId || conversation_id || 'conv_default_001';
  const selectedCustomerId = customerId || customer_id || 'cust_1001';

  // 2. Call ai.service.js (Zero Axios calls directly in controller)
  const aiResult = await aiService.chat({
    message: message.trim(),
    conversation_id: selectedConversationId,
    customer_id: selectedCustomerId
  });

  // 3. Return Standardized Response
  if (res.ok) {
    return res.ok(aiResult, 'AI response processed successfully');
  }

  return res.status(200).json({
    success: true,
    message: 'AI response processed successfully',
    data: aiResult,
    errors: null
  });
});

/**
 * @desc Get AI chat service status
 * @route GET /api/v1/chat/health
 * @access Public / Authenticated
 */
export const getChatHealth = asyncHandler(async (req, res, next) => {
  const healthData = await aiService.health();

  if (res.ok) {
    return res.ok(healthData, 'Chat AI service status retrieved successfully');
  }

  return res.status(200).json({
    success: true,
    message: 'Chat AI service status retrieved successfully',
    data: healthData,
    errors: null
  });
});

/**
 * @desc Get chat history list
 * @route GET /api/v1/chat/history
 * @access Public / Authenticated
 */
export const getChatHistory = asyncHandler(async (req, res, next) => {
  const historyData = [
    {
      id: 'msg_101',
      sender: 'user',
      text: 'Hello, I need help with my enterprise subscription refund.',
      timestamp: new Date(Date.now() - 600000).toISOString()
    },
    {
      id: 'msg_102',
      sender: 'ai_agent',
      text: 'Hello from AI Service! I can assist you with your refund inquiry.',
      timestamp: new Date(Date.now() - 580000).toISOString()
    }
  ];

  if (res.ok) {
    return res.ok(historyData, 'Chat history retrieved successfully');
  }

  return res.status(200).json({
    success: true,
    message: 'Chat history retrieved successfully',
    data: historyData,
    errors: null
  });
});

export default {
  sendChatMessage,
  getChatHealth,
  getChatHistory
};
