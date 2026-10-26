import sqlite3
from authentication.authentication import password_hash

database_connection = "database/database.db"

def get_database_connection():
    return(sqlite3.connect(database_connection))


def create_tables():
    connection = get_database_connection()
    cursor = connection.cursor()



    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    second_name TEXT NOT NULL,
    email TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    employee_type TEXT NOT NULL 
    CHECK (employee_type IN (
        "employee",
        "team leader",
        "manager",
        "administrator"
        ))
    )
    """
    )
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    description TEXT,
    manager_id INTEGER NOT NULL,
    status TEXT NOT NULL 
        CHECK (status IN (
        "not started",
        "in progress",
        "completed"
        )),
        FOREIGN KEY (manager_id) REFERENCES employees(id)
        )
    """
    )
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        employee_id INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (employee_id) REFERENCES employees(id)
    )
    """)

   
    connection.commit()
    connection.close()

def get_employee_by_email(email):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM employees WHERE email = ?
    """,
    (email,))
    employee = cursor.fetchone()

    connection.close()

    return employee
def get_projects_for_manager(manager_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM projects WHERE manager_id = ?
    """,(manager_id,))

    projects = cursor.fetchall()

    connection.close()

    return projects 
def get_projects_for_employee(employee_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT projects.*
    FROM projects
    JOIN project_members
        ON projects.id = project_members.project_id
    WHERE project_members.employee_id = ?
    """, (employee_id,))

    projects = cursor.fetchall()
    connection.close()

    return projects


###Basis to provide test data for the database for testing purposes
def add_simulated_data_to_db():
    connection = get_database_connection()
    cursor = connection.cursor()
    password1 = password_hash("Employee1?")
    password2 = password_hash("TeamLeader1?")
    password3 = password_hash("Manager1?")
    password4 = password_hash("Administrator1?")

    cursor.execute("""
    INSERT INTO employees (first_name, second_name, email,
    username, password, employee_type)
    VALUES (?,?,?,?,?,?)""",
    (
        ("Alex",
         "Smith",
         "alex.smith@makeitall.com",
         "alex_smith",
         password1,
         "employee" 
         
        )
    )
    )
    cursor.execute("""
        INSERT INTO employees (first_name, second_name, email,
        username, password, employee_type)
        VALUES (?,?,?,?,?,?)""",
        (
            ("John",
             "Paul",
             "john.paul@makeitall.com",
             "john_paul",
             password2,
             "team leader" 
             
            )
        )
        )
    cursor.execute("""
       INSERT INTO employees (first_name, second_name, email,
       username, password, employee_type)
       VALUES (?,?,?,?,?,?)""",
       (
           ("Sarah",
            "Jones",
            "sarah.jones@makeitall.com",
            "sarah_jones",
            password3,
            "manager" 
            
           )
       )
       )
    cursor.execute("""
        INSERT INTO employees (first_name, second_name, email,
        username, password, employee_type)
        VALUES (?,?,?,?,?,?)""",
        (
            ("Admin",
             "1",
             "admin@makeitall.com",
             "admin",
             password4,
             "administrator" 
             
            )
        )
        )
    connection.commit()
    connection.close()



create_tables()
#Added the simulated once (23.10.2026 15:10 ANORBS), now commented out
#employees simulated data
#employee - Alex, Smith,Email -  alex.smith@makeitall.com,Username -  alex_smith,Password - Employee1?,Role - employee
#teamleader - John, Paul,Email -  john.paul@makeitall.com,Username -  john_paul,Password - TeamLeader1?,Role - team leader
#manager - Sarah, Jones, Email - sarah.jones@makeitall.com,Username - sarah_jones,Passowrd - Manager1?,Role - manager
#admin - admin, 1, Email - admin@makeitall.com,Username - admin,Password - Administrator1?, Role - administrator
#add_simulated_data_to_db() - No need for method to be ran again
#projects table data also has been simulated
#project members table also been simulated
#install db viewer extension to view db
def select_all_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("""
    SELECT * FROM project_members
    """)
    data = cursor.fetchall()
    return data


