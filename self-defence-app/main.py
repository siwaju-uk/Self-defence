from app import app, socketio

# Export the Flask app for gunicorn
application = app

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)