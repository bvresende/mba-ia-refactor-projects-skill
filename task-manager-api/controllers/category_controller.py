from database import db
from models.category import Category
from models.task import Task
from sqlalchemy import func

class CategoryController:
    @staticmethod
    def get_categories():
        categories = Category.query.all()

        # Otimização de N+1 queries utilizando agregação em lote
        counts = dict(
            db.session.query(Task.category_id, func.count(Task.id))
            .filter(Task.category_id.isnot(None))
            .group_by(Task.category_id)
            .all()
        )

        result = []
        for c in categories:
            cat_data = c.to_dict()
            cat_data['task_count'] = counts.get(c.id, 0)
            result.append(cat_data)

        return result, 200

    @staticmethod
    def create_category(data):
        if not data:
            return {'error': 'Dados inválidos'}, 400

        name = data.get('name')
        if not name:
            return {'error': 'Nome é obrigatório'}, 400

        category = Category(
            name=name,
            description=data.get('description', ''),
            color=data.get('color', '#000000')
        )

        try:
            db.session.add(category)
            db.session.commit()
            return category.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {'error': 'Erro ao criar categoria'}, 500

    @staticmethod
    def update_category(cat_id, data):
        cat = db.session.get(Category, cat_id)
        if not cat:
            return {'error': 'Categoria não encontrada'}, 404
        if not data:
            return {'error': 'Dados inválidos'}, 400

        if 'name' in data:
            cat.name = data['name']
        if 'description' in data:
            cat.description = data['description']
        if 'color' in data:
            cat.color = data['color']

        try:
            db.session.commit()
            return cat.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Erro ao atualizar'}, 500

    @staticmethod
    def delete_category(cat_id):
        cat = db.session.get(Category, cat_id)
        if not cat:
            return {'error': 'Categoria não encontrada'}, 404

        try:
            db.session.delete(cat)
            db.session.commit()
            return {'message': 'Categoria deletada'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': 'Erro ao deletar'}, 500
