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

stmt['GET_PROJECT_HEATMAP_DATA'] = """
Select DATE, COUNT(edited_file) AS files_count FROM (
SELECT DISTINCT DATE(start_date) AS date, edited_file
FROM midnight
WHERE user_id IS (SELECT id FROM user WHERE username is :u)
AND INSTR(edited_file,
    CONCAT(:f, :p, "/")
)
)
GROUP BY 1
ORDER BY 1 DESC
LIMIT 364;
"""


def getUserActivity(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_USER_ACTIVITY'], {'p': user.project_folder,
                                            'u': user.username})


def getProjectActivity(username, projectname):
    user = getUserFromUsername(username)
    return eval(stmt['GET_PROJECT_ACTIVITY'], {'p': user.project_folder,
                                               'u': user.username,
                                               'f': projectname})


def getHeatMap(username, projectname=''):
    user = getUserFromUsername(username)
    return eval(stmt['GET_PROJECT_HEATMAP_DATA'], {'u': user.username,
                                                   'f': user.project_folder,
                                                   'p': projectname})


def getUserFromUsername(username) -> User:
    return User.query.filter(User.username == username).first()


def eval(stmt, p):
    return DB.execute(text(stmt), p).all()
