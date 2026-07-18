import express from 'express';
import * as chatController from '../controllers/chatController.js';
import { validateChatMessage } from '../validators/chatValidator.js';

const router = express.Router();

// GET /api/v1/chat/health
router.get('/health', chatController.getChatHealth);

// POST /api/v1/chat (validated payload parameters)
router.post('/', validateChatMessage, chatController.sendChatMessage);

// Backward Compatibility Routes
router.get('/history', chatController.getChatHistory);
router.post('/send', validateChatMessage, chatController.sendChatMessage);

export default router;
