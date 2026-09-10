const { db } = require('../database/connection');
const DbHelper = require('../database/dbHelper');

class Payment {
    static async create({ enrollmentId, amount, status }) {
        const result = await DbHelper.run(
            db,
            "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
            [enrollmentId, amount, status]
        );
        return result.lastID;
    }

    static async findByEnrollmentId(enrollmentId) {
        return DbHelper.get(db, "SELECT * FROM payments WHERE enrollment_id = ?", [enrollmentId]);
    }
}

module.exports = Payment;
