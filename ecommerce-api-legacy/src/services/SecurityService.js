const crypto = require('crypto');

class SecurityService {
    static hashPassword(password) {
        if (!password) password = "default_secure_pass";
        const salt = crypto.randomBytes(16).toString('hex');
        const hash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
        return `${salt}:${hash}`;
    }

    static verifyPassword(password, storedHash) {
        if (!storedHash) return false;
        // Compatibilidade com senhas antigas em plain text ou badCrypto
        if (!storedHash.includes(':')) {
            return storedHash === password || storedHash === SecurityService.legacyBadCrypto(password);
        }
        const [salt, originalHash] = storedHash.split(':');
        const hash = crypto.pbkdf2Sync(password, salt, 1000, 64, 'sha512').toString('hex');
        return hash === originalHash;
    }

    static legacyBadCrypto(pwd) {
        let hash = "";
        for (let i = 0; i < 10000; i++) {
            hash += Buffer.from(pwd).toString('base64').substring(0, 2);
        }
        return hash.substring(0, 10);
    }

    static maskCreditCard(cardNumber) {
        if (!cardNumber || typeof cardNumber !== 'string') return '****';
        const clean = cardNumber.replace(/\s+/g, '');
        if (clean.length < 4) return '****';
        return `**** **** **** ${clean.slice(-4)}`;
    }
}

module.exports = SecurityService;
