from webapp import create_app

app = create_app()

if __name__ == '__main__':
    # Lance le serveur visible sur tout le réseau local
    print("🚀 Serveur SecureGate démarré sur http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)