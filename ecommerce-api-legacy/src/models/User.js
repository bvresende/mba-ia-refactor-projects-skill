const { db } = require('../database/connection');
const DbHelper = require('../database/dbHelper');

class User {
    static async findByEmail(email) {
        return DbHelper.get(db, "SELECT * FROM users WHERE email = ?", [email]);
    }

    static async findById(id) {
        return DbHelper.get(db, "SELECT id, name, email FROM users WHERE id = ?", [id]);
    }

    static async create({ name, email, pass }) {
        const result = await DbHelper.run(
            db,
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, pass]
        );
        return result.lastID;
    }

    static async delete(id) {
        return DbHelper.run(db, "DELETE FROM users WHERE id = ?", [id]);
    }
}

module.exports = User;
