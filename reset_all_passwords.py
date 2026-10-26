from database.database import get_all_employees, set_employee
# __        __  _    ____  _   _ ___ _   _  ____ 
# \ \      / / / \  |  _ \| \ | |_ _| \ | |/ ___|
#  \ \ /\ / / / _ \ | |_) |  \| || ||  \| | |  _ 
#   \ V  V / / ___ \|  _ <| |\  || || |\  | |_| |
#    \_/\_/ /_/   \_\_| \_\_| \_|___|_| \_|\____|
"""
Running file resets ALL passwords in the entire database.
Admin password will be admin and every other user's password will be password.
This should NEVER be run in production.
"""

if __name__ == "__main__":
    print("Resetting all passwords in the database...")
    for e in get_all_employees():
        new_password = "admin1" if e[6] == "administrator" else "password"
        set_employee(e[1], e[2], e[3], e[4], new_password, role=e[6], employee_id=e[0])
        print("reset", e[3])
        
    print("Done.\nAdmin password is: admin1\nAll other passwords are: password")
