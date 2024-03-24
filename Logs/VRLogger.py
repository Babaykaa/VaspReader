import sqlite3


def sendDataToLogger(func=None, operation_type='program'):
    def wrapper(func):
        def wrapped_func(*args):
            try:
                args[0].get_logger().insert_logs(args[0].__class__.__name__, func.__name__, operation_type, 'IN PROGRESS')
            except AttributeError:
                pass
            output = func(*args)
            try:
                args[0].get_logger().insert_logs(args[0].__class__.__name__, func.__name__, operation_type)
            except AttributeError:
                pass
            return output
        return wrapped_func
    if func is not None:
        return wrapper(func)
    else:
        return wrapper


class VRLogger:

    def __init__(self, db_name='logs.db'):
        self._db = sqlite3.connect(f'Logs\\{db_name}')
        self._cursor = self._db.cursor()
        self.__operation_number = 1
        try:
            self._cursor.execute("SELECT * FROM logs LIMIT 13;").fetchall()
            self._cursor.execute("DELETE FROM logs;").fetchall()
            self._db.commit()
        except sqlite3.OperationalError:
            self._cursor.execute("CREATE TABLE logs ( NUMBER int NOT NULL UNIQUE, WINDOW text NOT NULL, "
                                 "OPERATION text NOT NULL, OPERATION_TYPE text NOT NULL, "
                                 "RESULT text NOT NULL DEFAULT 'SUCCESS', CAUSE text DEFAULT NULL, DATE date NOT NULL, "
                                 "TIME time NOT NULL, CHECK (OPERATION_TYPE IN ('user', 'program')), "
                                 "CHECK (RESULT IN ('FAILED', 'IN PROGRESS', 'SUCCESS')), "
                                 "PRIMARY KEY (NUMBER) );").fetchall()

    def insert_logs(self, window: str, operation: str, operation_type: str = 'program', result: str = 'SUCCESS', cause: str = None):
        if cause is not None:
            self._cursor.execute(f"INSERT INTO logs VALUES ('{self.__operation_number}', '{window}', '{operation}', '{operation_type}', '{result}', '{cause}', current_date, current_time);").fetchall()
        else:
            self._cursor.execute(f"INSERT ")
        self._db.commit()
        self.__operation_number += 1

    def __del__(self):
        self._cursor.close()
        self._db.close()
