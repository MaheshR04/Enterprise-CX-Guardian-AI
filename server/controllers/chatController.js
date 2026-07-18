import asyncHandler from '../utils/asyncHandler.js';

/**
 * @desc Get chat history list
 * @route GET /api/v1/chat/history
 */
export const getChatHistory = asyncHandler(async (req, res, next) => {
  res.ok([], "Chat History API Working - Controller Active");
});

/**
 * @desc Send message to assistant
 * @route POST /api/v1/chat/send
 */
export const sendChatMessage = asyncHandler(async (req, res, next) => {
  res.ok({}, "Chat Message Send API Working - Controller Active");
});
