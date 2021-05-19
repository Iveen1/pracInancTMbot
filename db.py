import sqlite3

class BotDB():
    def __init__(self):
        self.db = sqlite3.connect('database.db')
        self.sql = self.db.cursor()


    def addTodo(self, userId, userLogin, userName, description):
        self.sql.execute(f"SELECT * FROM users WHERE userId = '{userId}'")
        todoId = len(self.sql.fetchall())+1
        self.sql.execute(f"INSERT INTO users(userId, userLogin, userName, todoId, description) VALUES (?, ?, ?, ?, ?)", (userId, userLogin, userName, todoId, description))
        self.db.commit()
        return True


    def getTodosByUserId(self, userId, status):
        self.sql.execute(f"SELECT * FROM users WHERE userId = '{userId}' AND status = '{status}'")
        return self.sql.fetchall()


    def completeTodoByIds(self, userId, todoId):
        self.sql.execute(f"SELECT * FROM users WHERE userId = '{userId}' AND todoId = '{todoId}'")
        result = self.sql.fetchone()
        if result == None:
            return None

        elif result[3] == 0:
            return False
        else:
            self.sql.execute(f"UPDATE users SET ('status') = ('0') WHERE userId = '{userId}' AND todoId = '{todoId}'")
            self.db.commit()
            return True

    def insertTimeByIds(self, userId, todoId, value):
        self.sql.execute(f"UPDATE users SET ('startTime') = '{value}' WHERE userId = '{userId}' and todoId = '{todoId}'")
        self.db.commit()
        return True

    def getRowsWithTime(self):
        self.sql.execute(f"SELECT * FROM users WHERE startTime != 'None' AND notificationDeliveryStatus ='0'")
        return self.sql.fetchall()

    def updateNotificationDeliveryStatusByIds(self, userId, todoId):
        self.sql.execute(f"UPDATE users SET ('notificationDeliveryStatus') = '{1}' WHERE userId = '{userId}' and todoId = '{todoId}'")
        self.db.commit()
        return True