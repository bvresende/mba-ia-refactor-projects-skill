const express = require('express');
const router = express.Router();
const ReportController = require('../controllers/ReportController');

router.get('/admin/financial-report', ReportController.financialReport);

module.exports = router;
