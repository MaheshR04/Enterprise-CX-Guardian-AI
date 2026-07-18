import express from 'express';
import * as customerController from '../controllers/customerController.js';

const router = express.Router();

router.get('/', customerController.getCustomers);
router.get('/:id', customerController.getCustomerById);

export default router;
