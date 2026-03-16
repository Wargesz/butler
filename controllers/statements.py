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
        ORDER BY 2 DESC;
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
    AND start_date > DATE("now", "-1 year")
)
GROUP BY 1
ORDER BY 1 DESC;
"""

stmt['GET_PROJECT_HEATMAP_DATA'] = """
SELECT DATE, COUNT(edited_file) AS files_count FROM (
SELECT DISTINCT DATE(start_date) AS date, edited_file
FROM midnight
WHERE user_id IS :i
AND INSTR(edited_file,
    CONCAT(:f, :p, "/")
)
AND start_date > DATE("now", "-1 year")
)
GROUP BY 1
ORDER BY 1 DESC;
"""

stmt['GET_EDITOR_DATA'] = """
SELECT editor, SUM(seconds)
FROM midnight
WHERE user_id == :i
GROUP BY 1
ORDER BY 1 DESC;
"""

stmt['GET_TOTAL_HEATMAP_WEEKLY_DATA'] = """
SELECT strftime('%Y-%m-%d', start_date) AS first_log_of_the_week,
SUM(seconds) AS seconds
FROM midnight
WHERE user_id == :i
AND instr(edited_file, :p)
GROUP BY strftime('%Y-%W', start_date);
"""

stmt['GET_PROJECT_WEEKLY_DATA'] = """
SELECT strftime('%Y-%m-%d', start_date) AS first_log_of_the_week,
SUM(seconds) AS seconds
FROM midnight
WHERE user_id == :i
AND INSTR(edited_file,
    CONCAT(:f, :p, "/")
)
GROUP BY strftime('%Y-%W', start_date);
"""

stmt['GET_SCOPE_DATA'] = """
SELECT replace(edited_file, :p, ""), SUM(seconds) as seconds
FROM midnight
WHERE date(start_date) >= :fd
AND date(start_date) <= :td
AND user_id == :i
AND instr(edited_file, :p)
GROUP BY 1;
"""


stmt['GET_BEST_MONTH'] = """
SELECT strftime("%Y-%m", start_date) as date, sum(seconds) as seconds
FROM midnight
WHERE user_id == :i
AND instr(edited_file, :p)
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1;
"""


stmt['GET_BEST_WEEK'] = """
SELECT strftime("%Y-%m-%d", start_date) as date, sum(seconds) as seconds
FROM midnight
WHERE user_id == :i
AND instr(edited_file, :p)
GROUP BY strftime("%Y-%W", start_date)
ORDER BY 2 DESC
LIMIT 1;
"""


stmt['GET_BEST_DAY'] = """
SELECT strftime("%Y-%m-%d", start_date) as date, sum(seconds) as seconds
FROM midnight
WHERE user_id == :i
AND instr(edited_file, :p)
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1
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


def getUserWeeklyActivity(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_TOTAL_HEATMAP_WEEKLY_DATA'],
                {'i': user.id, 'p': user.project_folder})


def getProjectWeeklyActivity(username, projectname):
    user = getUserFromUsername(username)
    return eval(stmt['GET_PROJECT_WEEKLY_DATA'],
                {'i': user.id, 'f': user.project_folder, 'p': projectname})


def getScopeData(username, fromDate, toDate):
    user = getUserFromUsername(username)
    return eval(stmt['GET_SCOPE_DATA'], {'i': user.id, 'p': user.project_folder,
                                         'fd': fromDate, 'td': toDate})


def getBestMonth(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_BEST_MONTH'], {'i': user.id, 'p': user.project_folder})


def getBestDay(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_BEST_DAY'], {'i': user.id, 'p': user.project_folder})


def getBestWeek(username):
    user = getUserFromUsername(username)
    return eval(stmt['GET_BEST_WEEK'], {'i': user.id, 'p': user.project_folder})


def getUserFromUsername(username) -> User:
    return User.query.filter(User.username == username).first()


def eval(stmt, p):
    return DB.execute(text(stmt), p).all()
