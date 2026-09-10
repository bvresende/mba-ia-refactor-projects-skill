const { db } = require('../database/connection');
const DbHelper = require('../database/dbHelper');

class Course {
    static async findActiveById(id) {
        return DbHelper.get(db, "SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
    }

    static async findAll() {
        return DbHelper.all(db, "SELECT * FROM courses", []);
    }
}

module.exports = Course;
