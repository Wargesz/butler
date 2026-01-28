from models.models import User
from sqlalchemy.sql import text
from controllers.db import DB

stmt = {}

stmt['GET_USER_ACTIVITY'] = """
SELECT SUBSTR(REPLACE(edited_file, :p, ""), 0,
        INSTR(REPLACE(edited_file, :p, ""), "/")) AS project,
        SUM(seconds) AS total_time
        FROM midnight
        WHERE user_id == :i
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 10;
"""

stmt['GET_PROJECT_ACTIVITY'] = """
SELECT replace(edited_file, CONCAT(:f, :p, "/"), "") as file,
SUM(seconds) AS total_time
FROM midnight
WHERE user_id == :i
AND INSTR(edited_file,
    CONCAT(:f, :p, "/")
)
GROUP BY 1
ORDER BY 2 DESC;
"""

stmt['GET_TOTAL_HEATMAP_DATA'] = """
SELECT date, COUNT(edited_file) FROM  (
    SELECT DISTINCT DATE(start_date) as date, edited_file
    FROM midnight
    WHERE user_id == :i
)
GROUP BY 1
ORDER BY 1 DESC
LIMIT 364;
"""

stmt['GET_PROJECT_HEATMAP_DATA'] = """
Select DATE, COUNT(edited_file) AS files_count FROM (
SELECT DISTINCT DATE(start_date) AS date, edited_file
FROM midnight
WHERE user_id IS :i
AND INSTR(edited_file,
    CONCAT(:f, :p, "/")
)
)
GROUP BY 1
ORDER BY 1 DESC
LIMIT 364;
"""

stmt['GET_EDITOR_DATA'] = """
SELECT editor, SUM(seconds)
FROM midnight
WHERE user_id == :i
GROUP BY 1
ORDER BY 1 DESC;
"""


def getUserActivity(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_USER_ACTIVITY'], {'p': user.project_folder,
                                            'i': user.id})


def getUserHeatMap(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_TOTAL_HEATMAP_DATA'], {'i': user.id})


def getProjectActivity(username, projectname):
    user = getUserFromUsername(username)
    return eval(stmt['GET_PROJECT_ACTIVITY'], {'f': user.project_folder,
                                               'i': user.id,
                                               'p': projectname})


def getHeatMap(username, projectname=''):
    user = getUserFromUsername(username)
    return eval(stmt['GET_PROJECT_HEATMAP_DATA'], {'i': user.id,
                                                   'f': user.project_folder,
                                                   'p': projectname})


def getEditorData(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_EDITOR_DATA'], {'i': user.id})


def getUserFromUsername(username) -> User:
    return User.query.filter(User.username == username).first()


def eval(stmt, p):
    return DB.execute(text(stmt), p).all()
