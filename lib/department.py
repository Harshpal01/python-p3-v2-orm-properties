# lib/department.py
from __init__ import CURSOR, CONN

class Department:

    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name  # Triggers validation
        self.location = location  # Triggers validation

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    # Property for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise ValueError("Name must be a string.")
        if len(value.strip()) == 0:
            raise ValueError("Name cannot be an empty string.")
        self._name = value

    # Property for location
    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if not isinstance(value, str):
            raise ValueError("Location must be a string.")
        if len(value.strip()) == 0:
            raise ValueError("Location cannot be an empty string.")
        self._location = value

    @classmethod
    def create_table(cls):
        """Create a new table to persist the attributes of Department instances"""
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drop the table that persists Department instances"""
        sql = "DROP TABLE IF EXISTS departments;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Insert a new row and store the object in the `all` dictionary"""
        sql = "INSERT INTO departments (name, location) VALUES (?, ?)"
        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()
        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, location):
        """Create and save a new Department instance"""
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the row for this Department in the database"""
        sql = "UPDATE departments SET name = ?, location = ? WHERE id = ?"
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete the row from the database and remove from memory"""
        sql = "DELETE FROM departments WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        type(self).all.pop(self.id, None)
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Return a Department object with attributes from a DB row"""
        department = cls.all.get(row[0])
        if department:
            department.name = row[1]
            department.location = row[2]
        else:
            department = cls(row[1], row[2], id=row[0])
            cls.all[department.id] = department
        return department

    @classmethod
    def get_all(cls):
        """Return a list of all Department objects from the table"""
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Return a Department by its ID"""
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Return a Department by name"""
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

    def employees(self):
        """Return a list of Employees in this Department"""
        from employee import Employee
        sql = "SELECT * FROM employees WHERE department_id = ?"
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Employee.instance_from_db(row) for row in rows]
