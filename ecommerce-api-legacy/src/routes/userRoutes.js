const express = require('express');
const router = express.Router();
const UserController = require('../controllers/UserController');

router.delete('/users/:id', UserController.deleteUser);

module.exports = router;
