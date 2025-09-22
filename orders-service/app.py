# orders-service/app.py

from flask import Flask, request, jsonify
import requests
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

USER_SERVICE_URL = "http://localhost:5001"

orders_db = {
    1: {
        "id": 1,
        "user_id": 1,
        "product": "Laptop HP Pavilion",
        "quantity": 1,
        "price": 1200.00,
        "status": "completed",
        "created_at": "2025-01-15T10:30:00"
    },
    2: {
        "id": 2,
        "user_id": 2,
        "product": "Mouse Inalambrico",
        "quantity": 2,
        "price": 25.00,
        "status": "pending",
        "created_at": "2025-01-16T14:20:00"
    },
    3: {
        "id": 3,
        "user_id": 1,
        "product": "Teclado Mecanico",
        "quantity": 1,
        "price": 150.00,
        "status": "shipped",
        "created_at": "2025-01-17T09:15:00"
    }
}

def verify_user_exists(user_id):
    try:
        response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        logger.error(f"Error verificando usuario {user_id}: {str(e)}")
        return False, None

@app.route('/health', methods=['GET'])
def health_check():
    try:
        response = requests.get(f"{USER_SERVICE_URL}/health", timeout=3)
        users_service_status = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        users_service_status = "unreachable"
    
    return jsonify({
        "status": "healthy",
        "service": "orders-service",
        "dependencies": {"users-service": users_service_status},
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/orders', methods=['GET'])
def get_orders():
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status')
    
    orders = list(orders_db.values())
    if user_id:
        orders = [order for order in orders if order['user_id'] == user_id]
    if status:
        orders = [order for order in orders if order['status'] == status]
    
    return jsonify({
        "orders": orders,
        "count": len(orders),
        "service": "orders-service",
        "filters_applied": {"user_id": user_id, "status": status}
    })

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_db.get(order_id)
    if order:
        return jsonify(order)
    return jsonify({"error": "Pedido no encontrado", "order_id": order_id}), 404

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        required_fields = ['user_id', 'product', 'quantity', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400
        
        user_id = data['user_id']
        user_exists, user_data = verify_user_exists(user_id)
        
        if not user_exists:
            return jsonify({
                "error": "Usuario no encontrado o servicio no disponible",
                "user_id": user_id,
                "service_communication": "failed"
            }), 400
        
        if not user_data.get('active', True):
            return jsonify({"error": "El usuario esta inactivo", "user_id": user_id}), 400
        
        new_id = max(orders_db.keys()) + 1 if orders_db else 1
        new_order = {
            "id": new_id,
            "user_id": user_id,
            "product": data['product'],
            "quantity": int(data['quantity']),
            "price": float(data['price']),
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        orders_db[new_id] = new_order
        
        return jsonify({
            "order": new_order,
            "user_info": {"name": user_data['name'], "email": user_data['email']},
            "service_communication": "success"
        }), 201
    except ValueError as e:
        return jsonify({"error": f"Datos invalidos: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error al crear pedido: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/orders/<int:order_id>/details', methods=['GET'])
def get_order_with_user_details(order_id):
    order = orders_db.get(order_id)
    if not order:
        return jsonify({"error": "Pedido no encontrado"}), 404
    
    user_exists, user_data = verify_user_exists(order['user_id'])
    response_data = {"order": order}
    
    if user_exists:
        response_data["user_details"] = user_data
        response_data["communication_status"] = "success"
    else:
        response_data["user_details"] = None
        response_data["communication_status"] = "failed"
    
    return jsonify(response_data)

@app.route('/orders/stats', methods=['GET'])
def get_order_stats():
    total_orders = len(orders_db)
    total_revenue = sum(order['price'] * order['quantity'] for order in orders_db.values())
    
    status_count = {}
    for order in orders_db.values():
        status = order['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    return jsonify({
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "orders_by_status": status_count,
        "average_order_value": round(total_revenue / total_orders if total_orders > 0 else 0, 2),
        "service": "orders-service"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
