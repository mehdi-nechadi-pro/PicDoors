from webapp import create_app

app = create_app()

# --- DÉMARRAGE ---
if __name__ == '__main__':
    # On utilise le port 5001 pour éviter le conflit AirPlay (Port 5000)
    print("Serveur Flask démarré sur http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)