from flask import Flask
from flask_bcrypt import Bcrypt

from config import Config

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.nutrition import nutrition_bp
from routes.profile import profile_bp
from routes.ai import ai_bp
from routes.pose import pose_bp

app = Flask(__name__)
app.config.from_object(Config)

bcrypt = Bcrypt(app)

print(app.url_map)

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(nutrition_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(pose_bp)

if __name__ == "__main__":
    app.run(debug=True)