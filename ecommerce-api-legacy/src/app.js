const express = require('express');
const config = require('./config');
const { initDb } = require('./database/connection');
const apiRoutes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

// Registro de rotas desacopladas
app.use('/api', apiRoutes);

// Middleware centralizado de tratamento de erros
app.use(errorHandler);

// Inicialização assíncrona do banco e servidor
async function startServer() {
    try {
        await initDb();
        const server = app.listen(config.port, () => {
            console.log(`LMS API (Arquitetura MVC Refatorada) rodando na porta ${config.port}...`);
        });
        return { app, server };
    } catch (error) {
        console.error("Falha ao inicializar o servidor:", error);
        process.exit(1);
    }
}

if (require.main === module) {
    startServer();
}

module.exports = { app, startServer };
