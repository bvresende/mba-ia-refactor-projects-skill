function errorHandler(err, req, res, next) {
    console.error("[ERROR]", err.message || err);
    const status = err.status || 500;
    res.status(status).send(err.message || "Erro interno do servidor");
}

module.exports = errorHandler;
