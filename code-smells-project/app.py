import sys
import os

# Adiciona o diretório atual ao sys.path para garantir resolução dos módulos de src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import create_app
from src.database.db import init_db
from src.config.settings import settings

app = create_app()

if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("SERVIDOR INICIADO (ARQUITETURA MVC)")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
