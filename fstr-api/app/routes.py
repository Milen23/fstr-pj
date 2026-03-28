from flask import Blueprint, request, jsonify
from app.schemas import PerevalSubmitSchema, PerevalUpdateSchema
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
# ========== МЕТОД 1: POST /submitData (из 1 спринта) ==========
@bp.route('/submitData', methods=['POST'])
def submit_data():
    """
    Добавление нового перевала
    """
    try:
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


# ========== МЕТОД 2: GET /submitData/<id> ==========
@bp.route('/submitData/<int:pereval_id>', methods=['GET'])
def get_pereval(pereval_id):
    """
    Получение информации о перевале по ID
    """
    try:
        success, result = PerevalData.get_pereval_by_id(pereval_id)

        if success:
            return jsonify({
                "status": 200,
                "message": "ok",
                "pereval": result
            }), 200
        else:
            return jsonify({
                "status": 404,
                "message": result,  # result содержит сообщение об ошибке
                "pereval": None
            }), 404

    except Exception as e:
        logger.error(f"Unexpected error in get_pereval: {str(e)}")
        return jsonify({
            "status": 500,
            "message": f"Internal server error: {str(e)}",
            "pereval": None
        }), 500


# ========== МЕТОД 3: PATCH /submitData/<id> ==========
@bp.route('/submitData/<int:pereval_id>', methods=['PATCH'])
def update_pereval(pereval_id):
    """
    Обновление перевала (только если статус 'new')
    Нельзя обновлять: ФИО, email, телефон
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "state": 0,
                "message": "Bad Request: No JSON data provided"
            }), 400

        # Валидация данных для обновления
        schema = PerevalUpdateSchema()
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            logger.warning(f"Validation error in update: {e.messages}")
            return jsonify({
                "state": 0,
                "message": f"Validation error: {e.messages}"
            }), 400

        # Проверяем, нет ли попытки обновить запрещенные поля
        if 'user' in validated_data:
            return jsonify({
                "state": 0,
                "message": "Cannot update user information (name, email, phone)"
            }), 400

        # Обновляем данные
        success, message = PerevalData.update_pereval(pereval_id, validated_data)

        if success:
            return jsonify({
                "state": 1,
                "message": message
            }), 200
        else:
            # Определяем HTTP код по сообщению
            if "not found" in message.lower():
                return jsonify({
                    "state": 0,
                    "message": message
                }), 404
            elif "status is not 'new'" in message.lower():
                return jsonify({
                    "state": 0,
                    "message": message
                }), 400
            else:
                return jsonify({
                    "state": 0,
                    "message": message
                }), 500

    except Exception as e:
        logger.error(f"Unexpected error in update_pereval: {str(e)}")
        return jsonify({
            "state": 0,
            "message": f"Internal server error: {str(e)}"
        }), 500


# ========== МЕТОД 4: GET /submitData/?user__email=<email> ==========
@bp.route('/submitData/', methods=['GET'])
def get_perevals_by_user():
    """
    Получение списка перевалов пользователя по email
    """
    try:
        email = request.args.get('user__email')

        if not email:
            return jsonify({
                "status": 400,
                "message": "Bad Request: user__email parameter is required",
                "perevals": []
            }), 400

        success, result = PerevalData.get_perevals_by_user_email(email)

        if success:
            return jsonify({
                "status": 200,
                "message": "ok",
                "perevals": result
            }), 200
        else:
            return jsonify({
                "status": 404,
                "message": result,
                "perevals": []
            }), 404

    except Exception as e:
        logger.error(f"Unexpected error in get_perevals_by_user: {str(e)}")
        return jsonify({
            "status": 500,
            "message": f"Internal server error: {str(e)}",
            "perevals": []
        }), 500
