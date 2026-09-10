const { db } = require('../database/connection');
const DbHelper = require('../database/dbHelper');

class AuditLog {
    static async create(action) {
        return DbHelper.run(
            db,
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
    }
}

module.exports = AuditLog;
