# tests/test_microservices.py

import requests
import json
import time
from datetime import datetime

USERS_SERVICE = "http://localhost:5001"
ORDERS_SERVICE = "http://localhost:5002"

def print_separator(title):
    print("\n" + "="*60)
    print(f"{title}")
    print("="*60)

def print_result(description, response):
    print(f"\n{description}")
    print(f"Status: {response.status_code}")
    if response.status_code in (200, 201):
        print("Resultado: EXITOSO")
    else:
        print("Resultado: ERROR")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 40)

def test_services_health():
    print_separator("VERIFICACION DE SERVICIOS")
    try:
        response = requests.get(f"{USERS_SERVICE}/health", timeout=5)
        print_result("Health Check - Servicio de Usuarios", response)
        response = requests.get(f"{ORDERS_SERVICE}/health", timeout=5)
        print_result("Health Check - Servicio de Pedidos", response)
        return True
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar a los servicios")
        return False

def test_basic_functionality():
    print_separator("PRUEBAS BASICAS")
    response = requests.get(f"{USERS_SERVICE}/users")
    print_result("1. Obtener todos los usuarios", response)
    response = requests.get(f"{USERS_SERVICE}/users/1")
    print_result("2. Obtener usuario ID: 1", response)
    response = requests.get(f"{ORDERS_SERVICE}/orders")
    print_result("3. Obtener todos los pedidos", response)
    response = requests.get(f"{ORDERS_SERVICE}/orders/stats")
    print_result("4. Estadisticas de pedidos", response)

def test_microservices_communication():
    print_separator("COMUNICACION ENTRE MICROSERVICIOS")
    new_user = {
        "name": "Ana Martinez",
        "email": f"ana.{int(time.time())}@email.com"
    }
    response = requests.post(f"{USERS_SERVICE}/users", json=new_user)
    print_result("Crear nuevo usuario", response)
    if response.status_code == 201:
        user_data = response.json()
        new_user_id = user_data['id']
        new_order = {
            "user_id": new_user_id,
            "product": "Smartphone Samsung Galaxy",
            "quantity": 1,
            "price": 899.99
        }
        response = requests.post(f"{ORDERS_SERVICE}/orders", json=new_order)
        print_result("Crear pedido para usuario nuevo", response)
        response = requests.get(f"{ORDERS_SERVICE}/orders/1/details")
        print_result("Pedido con detalles de usuario", response)

def test_error_scenarios():
    print_separator("PRUEBAS DE MANEJO DE ERRORES")
    invalid_order = {
        "user_id": 999,
        "product": "Producto Test",
        "quantity": 1,
        "price": 50.00
    }
    response = requests.post(f"{ORDERS_SERVICE}/orders", json=invalid_order)
    print_result("Crear pedido para usuario inexistente", response)
    incomplete_order = {"user_id": 1}
    response = requests.post(f"{ORDERS_SERVICE}/orders", json=incomplete_order)
    print_result("Crear pedido con datos incompletos", response)
    response = requests.get(f"{USERS_SERVICE}/users/999")
    print_result("Obtener usuario inexistente", response)

def main():
    print("SISTEMA DE PRUEBAS PARA MICROSERVICIOS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if not test_services_health():
        return
    print("\nEjecutando suite completa de pruebas...")
    try:
        test_basic_functionality()
        test_microservices_communication()
        test_error_scenarios()
        print_separator("RESUMEN FINAL")
        print("Todas las pruebas completadas exitosamente")
    except Exception as e:
        print(f"\nError durante las pruebas: {e}")

if __name__ == "__main__":
    main()
