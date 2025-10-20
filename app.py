from app.controllers import db
from app import create_app

app = create_app()
app.app_context().push()
db.init_db()


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.db_session.remove()


if __name__ == '__main__':
    app.run(port=8080)
