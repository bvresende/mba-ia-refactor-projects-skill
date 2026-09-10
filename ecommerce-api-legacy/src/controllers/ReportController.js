const Course = require('../models/Course');
const Enrollment = require('../models/Enrollment');
const Payment = require('../models/Payment');
const User = require('../models/User');

class ReportController {
    static async financialReport(req, res, next) {
        try {
            const courses = await Course.findAll();
            const report = [];

            for (const c of courses) {
                const courseData = { course: c.title, revenue: 0, students: [] };
                const enrollments = await Enrollment.findByCourseId(c.id);

                for (const enr of enrollments) {
                    const user = await User.findById(enr.user_id);
                    const payment = await Payment.findByEnrollmentId(enr.id);

                    if (payment && payment.status === 'PAID') {
                        courseData.revenue += payment.amount;
                    }

                    courseData.students.push({
                        student: user ? user.name : 'Unknown',
                        paid: payment ? payment.amount : 0
                    });
                }

                report.push(courseData);
            }

            return res.json(report);
        } catch (error) {
            next(error);
        }
    }
}

module.exports = ReportController;
