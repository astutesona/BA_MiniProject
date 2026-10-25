import os
from flask import Flask, render_template
from config import config
from app.extensions import db, login_manager, csrf

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # User loader callback
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Template Jinja filters
    @app.template_filter('currency')
    def currency_filter(val):
        if val is None:
            return "$0.00"
        try:
            return f"${float(val):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.template_filter('number')
    def number_filter(val):
        if val is None:
            return "0"
        try:
            return f"{int(val):,}"
        except (ValueError, TypeError):
            return "0"

    @app.template_filter('percentage')
    def percentage_filter(val):
        if val is None:
            return "0.0%"
        try:
            return f"{float(val):.1f}%"
        except (ValueError, TypeError):
            return "0.0%"

    @app.template_filter('datetime_fmt')
    def datetime_filter(val, fmt='%b %d, %Y'):
        if not val:
            return "-"
        return val.strftime(fmt)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.customers import customers_bp
    from app.routes.products import products_bp
    from app.routes.categories import categories_bp
    from app.routes.orders import orders_bp
    from app.routes.analytics import analytics_bp
    from app.routes.inventory import inventory_bp
    from app.routes.targets import targets_bp
    from app.routes.reports import reports_bp
    from app.routes.query_lab import query_lab_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(targets_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(query_lab_bp)
    app.register_blueprint(users_bp)

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
