from flask import Blueprint, request, jsonify
from app.schemas import PerevalSubmitSchema
from app.database import PerevalData
from marshmallow import ValidationError
import logging

bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@bp.route('/submitData', methods=['POST'])
def submit_data():
    """
    Метод для добавления информации о новом перевале
    """
    try:
        # Получаем JSON из запроса
        data = request.get_json()

        if not data:
            return jsonify({
                "status": 400,
                "message": "Bad Request: No JSON data provided",
                "id": None
            }), 400

        # Валидация данных
        schema = PerevalSubmitSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            logger.warning(f"Validation error: {e.messages}")
            return jsonify({
                "status": 400,
                "message": f"Bad Request: {e.messages}",
                "id": None
            }), 400

        # Добавляем данные в БД
        success, message, pereval_id = PerevalData.add_pereval(validated_data)

        if success:
            return jsonify({
                "status": 200,
                "message": message,
                "id": pereval_id
            }), 200
        else:
            return jsonify({
                "status": 500,
                "message": message,
                "id": None
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in submitData: {str(e)}")
        return jsonify({
            "status": 500,
            "message": f"Internal server error: {str(e)}",
            "id": None
        }), 500


# Дополнительный метод для проверки статуса (можно добавить позже)
@bp.route('/submitData/<int:pereval_id>', methods=['GET'])
def get_pereval_status(pereval_id):
    """Получение статуса модерации перевала"""
    from app.models import Pereval

    pereval = Pereval.query.get(pereval_id)
    if not pereval:
        return jsonify({
            "status": 404,
            "message": "Pereval not found",
            "id": pereval_id
        }), 404

    return jsonify({
        "status": 200,
        "message": "ok",
        "pereval": {
            "id": pereval.id,
            "status": pereval.status,
            "title": pereval.title
        }
    }), 200