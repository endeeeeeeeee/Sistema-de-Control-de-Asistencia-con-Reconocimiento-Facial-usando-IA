"""
Servidor mínimo de prueba para diagnosticar el problema
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Servidor funcionando!</h1><p>Si ves esto, Flask está funcionando correctamente.</p>'

@app.route('/test')
def test():
    return '<h1>Test OK</h1><p>El servidor responde correctamente.</p>'

if __name__ == '__main__':
    print("=" * 60)
    print("SERVIDOR MÍNIMO DE PRUEBA")
    print("=" * 60)
    print("\nIniciando servidor en http://localhost:5001")
    print("Prueba: http://localhost:5001/test")
    print("\nPresiona Ctrl+C para detener\n")
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)

