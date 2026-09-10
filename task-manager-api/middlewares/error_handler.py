from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Dados inválidos'}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(409)
    def conflict(error):
        return jsonify({'error': 'Conflito de dados'}), 409

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'error': 'Erro interno do servidor'}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        return jsonify({'error': str(e)}), 500
