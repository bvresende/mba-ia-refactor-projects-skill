const { db } = require('../database/connection');
const DbHelper = require('../database/dbHelper');

class Enrollment {
    static async create({ userId, courseId }) {
        const result = await DbHelper.run(
            db,
            "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
            [userId, courseId]
        );
        return result.lastID;
    }

    static async findByCourseId(courseId) {
        return DbHelper.all(db, "SELECT * FROM enrollments WHERE course_id = ?", [courseId]);
    }
}

module.exports = Enrollment;
