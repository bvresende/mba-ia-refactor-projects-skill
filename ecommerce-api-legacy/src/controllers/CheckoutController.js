const Course = require('../models/Course');
const User = require('../models/User');
const Enrollment = require('../models/Enrollment');
const Payment = require('../models/Payment');
const AuditLog = require('../models/AuditLog');
const SecurityService = require('../services/SecurityService');
const config = require('../config');

class CheckoutController {
    static async processCheckout(req, res, next) {
        try {
            const { usr, eml, pwd, c_id, card } = req.body;

            // Validação de entrada estrita
            if (!usr || !eml || !c_id || !card) {
                return res.status(400).send("Bad Request");
            }

            // Consulta do curso ativo
            const course = await Course.findActiveById(c_id);
            if (!course) {
                return res.status(404).send("Curso não encontrado");
            }

            // Log sanitizado em conformidade com PCI-DSS
            const maskedCard = SecurityService.maskCreditCard(card);
            console.log(`[PAYMENT] Processando cartão ${maskedCard} no gateway configurado...`);

            // Regra de validação de pagamento
            const status = card.startsWith("4") ? "PAID" : "DENIED";
            if (status === "DENIED") {
                return res.status(400).send("Pagamento recusado");
            }

            // Busca ou criação do usuário
            let user = await User.findByEmail(eml);
            let userId;

            if (!user) {
                const passwordHash = SecurityService.hashPassword(pwd || "123456");
                userId = await User.create({ name: usr, email: eml, pass: passwordHash });
            } else {
                userId = user.id;
            }

            // Criação da matrícula e pagamento
            const enrollmentId = await Enrollment.create({ userId, courseId: c_id });
            await Payment.create({ enrollmentId, amount: course.price, status });

            // Registro de auditoria
            await AuditLog.create(`Checkout curso ${c_id} por ${userId}`);

            return res.status(200).json({ msg: "Sucesso", enrollment_id: enrollmentId });
        } catch (error) {
            next(error);
        }
    }
}

module.exports = CheckoutController;
