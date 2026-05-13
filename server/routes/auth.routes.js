import { Router } from 'express';
import {
  getMe,
  login,
  logout,
  signup,
  updateGuardianContacts,
} from '../controllers/auth.controller.js';
import { protect } from '../middleware/auth.middleware.js';
import { validate } from '../middleware/validate.middleware.js';
import {
  guardianContactsSchema,
  loginSchema,
  signupSchema,
} from '../validators/auth.validator.js';

const router = Router();

router.post('/signup', validate(signupSchema), signup);
router.post('/login', validate(loginSchema), login);
router.post('/logout', logout);
router.get('/me', protect, getMe);
router.put('/guardian-contacts', protect, validate(guardianContactsSchema), updateGuardianContacts);

export default router;
