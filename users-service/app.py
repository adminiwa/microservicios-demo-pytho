# users-service/app.py

from flask import Flask, request, jsonify
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

users_db = {
    1: {
        "id": 1,
        "name": "Juan Perez",
        "email": "juan@email.com",
        "created_at": "2025-01-10",
        "active": True
    },
    2: {
        "id": 2,
        "name": "Maria Gonzalez",
        "email": "maria@email.com",
        "created_at": "2025-01-12",
        "active": True
    },
    3: {
        "id": 3,
        "name": "Carlos Lopez",
        "email": "carlos@email.com",
        "created_at": "2025-01-15",
        "active": True
    }
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "users-service",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/users', methods=['GET'])
def get_users():
    active_users = [user for user in users_db.values() if user.get('active', True)]
    return jsonify({
        "users": active_users,
        "count": len(active_users),
        "service": "users-service"
    })

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users_db.get(user_id)
    if user:
        return jsonify(user)
    return jsonify({"error": "Usuario no encontrado", "user_id": user_id}), 404

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        if not data.get('name'):
            return jsonify({"error": "Campo requerido: name"}), 400
        if not data.get('email'):
            return jsonify({"error": "Campo requerido: email"}), 400
        
        for user in users_db.values():
            if user['email'] == data['email']:
                return jsonify({"error": "El email ya esta registrado"}), 409
        
        new_id = max(users_db.keys()) + 1 if users_db else 1
        new_user = {
            "id": new_id,
            "name": data['name'],
            "email": data['email'],
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "active": True
        }
        users_db[new_id] = new_user
        return jsonify(new_user), 201
    except Exception as e:
        logger.error(f"Error al crear usuario: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
