from flask import Blueprint
from src.video import router as video_router

api = Blueprint('api', __name__, url_prefix='/api')

api.register_blueprint(video_router)
