const express = require('express');
const router = express.Router();

const checkoutRoutes = require('./checkoutRoutes');
const reportRoutes = require('./reportRoutes');
const userRoutes = require('./userRoutes');

router.use(checkoutRoutes);
router.use(reportRoutes);
router.use(userRoutes);

module.exports = router;
