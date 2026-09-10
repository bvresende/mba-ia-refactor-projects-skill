const User = require('../models/User');

class UserController {
    static async deleteUser(req, res, next) {
        try {
            const { id } = req.params;
            await User.delete(id);
            return res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
        } catch (error) {
            next(error);
        }
    }
}

module.exports = UserController;
