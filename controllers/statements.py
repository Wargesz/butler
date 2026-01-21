from models.models import User
from sqlalchemy.sql import text
from controllers.db import DB

stmt = {}

stmt['GET_USER_ACTIVITY'] = """
SELECT substr(replace(edited_file, :p, ""), 0,
        instr(replace(edited_file, :p, ""), "/")) AS project,
        sum(seconds) AS total_time
        FROM midnight
        WHERE user_id == (SELECT id FROM user WHERE username == :u)
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 10;
"""

stmt['GET_PROJECT_ACTIVITY'] = """
SELECT substr(edited_file, length(concat(:p, "/", :f)) + 1) as file,
sum(seconds) AS total_time
FROM midnight
WHERE user_id == (SELECT id FROM user WHERE username == :u)
AND instr(edited_file, :f)
GROUP BY 1
ORDER BY 2 DESC;
"""


def getUserActivity(username):
    user = User.query.filter(User.username == username).first()
    return eval(stmt['GET_USER_ACTIVITY'], {'p': user.project_folder,
                                            'u': user.username})


def getProjectActivity(username, projectname):
    user = User.query.filter(User.username == username).first()
    return eval(stmt['GET_PROJECT_ACTIVITY'], {'p': user.project_folder,
                                               'u': user.username,
                                               'f': projectname})


def eval(stmt, p):
    return DB.execute(text(stmt), p).all()
