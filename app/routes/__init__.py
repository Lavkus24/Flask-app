from .scraping_routes import scraping_bp
from .comment_routes import comments_bp
from .profile_routes import search_bp
from .insight_routes import insight_bp
from .handle_insight_route import handle_insight_bp
# from .file_scrape_routes import handle_get_bp

def register_routes(app):
    app.register_blueprint(scraping_bp, url_prefix="/api")
    app.register_blueprint(comments_bp, url_prefix="/api")
    app.register_blueprint(search_bp, url_prefix="/api")
    app.register_blueprint(insight_bp,url_prefix="/api")
    app.register_blueprint(handle_insight_bp,url_prefix="/api")
    # app.register_blueprint(handle_get_bp,url_prefix="/api")
