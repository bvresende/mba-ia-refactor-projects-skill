const express = require('express');
const router = express.Router();
const CheckoutController = require('../controllers/CheckoutController');

router.post('/checkout', CheckoutController.processCheckout);

module.exports = router;
