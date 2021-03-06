from flask import render_template

from flask_app.app import db, app


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error_templates/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error_templates/500.html'), 500
