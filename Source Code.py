import csv
import os
from datetime import datetime, timedelta
DB_FILE = "users.csv"
EXP_PREFIX = "expenses_"
ADMIN_CONFIG = "admin.cfg"
ADMIN_KEY = "dayan@admin.com"
CATEGORIES = [
    "Food", "Transport", "Utilities", "Entertainment",
    "Health", "Education", "Shopping", "Bills",
    "Gifts", "Subscriptions", "Travel", "Other"
]
admin_user = "admin"
admin_pass = "admin123"
def load_admin_config():
    global admin_user, admin_pass
    if os.path.exists(ADMIN_CONFIG):
        with open(ADMIN_CONFIG, 'r') as f:
            creds = f.readlines()
            if len(creds) >= 2:
                admin_user = creds[0].strip()
                admin_pass = creds[1].strip()
    else:
        with open(ADMIN_CONFIG, 'w') as f:
            f.write(f"{admin_user}\n{admin_pass}\n")
def read_users():
    user_data = {}
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', newline='') as file:
            for u, p in csv.reader(file):
                user_data[u] = p
    return user_data
def register_user(username, password):
    with open(DB_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, password])
def safe_input(prompt, fallback=None):
    try:
        return input(prompt)
    except (EOFError, OSError):
        return fallback  
def login_flow():
    users = read_users()
    while True:
        print("\nExpense Tracker - Login Menu")
        print("1. New User Registration")
        print("2. Existing User Login")
        print("3. Admin Login (w/ Master Key)")
        choice = safe_input("Select an option [1-3]: ")
        if choice == '1':
            uname = safe_input("Choose a username: ")
            if not uname or uname in users or uname == admin_user:
                print("Username not available.")
                continue
            pw = safe_input("Set a password: ")
            if not pw:
                print("Password can't be empty.")
                continue
            register_user(uname, pw)
            print(f"Account for '{uname}' created. You can log in now.")
            users[uname] = pw  
        elif choice == '2':
            uname = safe_input("Username: ")
            pw = safe_input("Password: ")

            if uname == admin_user and pw == admin_pass:
                print(f"Welcome back, Admin '{uname}'!")
                run_admin()
            elif uname in users and users[uname] == pw:
                print(f"Hello {uname}, welcome!")
                user_panel(uname)
            else:
                print("Invalid login. Please retry.")
        elif choice == '3':
            key = safe_input("Enter Admin Key: ")
            if key == ADMIN_KEY:
                print("Master access granted.")
                run_admin()
            else:
                print("Access denied.")
        else:
            print("Pick a valid option please...")
def run_admin():
    users = read_users()
    while True:
        print("\nAdmin Control Panel")
        print("1. List Users")
        print("2. View Expenses for a User")
        print("3. Reset Password")
        print("4. Exit Admin Panel")
        choice = input("Choice: ")
        if choice == '1':
            if not users:
                print("No registered users.")
            else:
                print("\nUsers:")
                for u, p in users.items():
                    print(f" - {u} (password: {p})")   
        elif choice == '2':
            target = input("Username to inspect: ")
            if target in users:
                data = fetch_expenses(target)
                if not data:
                    print("No records found.")
                else:
                    for idx, d in enumerate(data, 1):
                        print(f"{idx}. [{d['date']}] {d['category']} - Rs. {d['amount']}")
            else:
                print("User not found.")
        elif choice == '3':
            user = input("Username for password reset: ")
            if user not in users:
                print("No such user.")
            else:
                new_pw = input(f"New password for {user}: ")
                if not new_pw:
                    print("Empty password is not allowed.")
                    continue
                users[user] = new_pw
                with open(DB_FILE, 'w', newline='') as f:
                    csv.writer(f).writerows(users.items())
                print("Password updated.")
        elif choice == '4':
            print("Exiting admin area.")
            break
        else:
            print("Try something valid.")
def fetch_expenses(user):
    path = f"{EXP_PREFIX}{user}.csv"
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return list(csv.DictReader(f))
def user_panel(user):
    expense_list = fetch_expenses(user)
    mode, max_budget = budget_setup()
    while True:
        print(f"\n{user}'s Dashboard")
        print("1. Add New Expense")
        print("2. Show All Expenses")
        print("3. Modify Existing Entry")
        print("4. Delete an Entry")
        print("5. Budget Status")
        print("6. Logout")
        opt = input("Select: ").strip()
        if opt == '1':
            record_expense(expense_list)
            store_expenses(user, expense_list)
        elif opt == '2':
            list_expenses(expense_list)
        elif opt == '3':
            modify_entry(expense_list)
            store_expenses(user, expense_list)
        elif opt == '4':
            remove_expense(expense_list)
            store_expenses(user, expense_list)
        elif opt == '5':
            left, spent = get_remaining_budget(expense_list, max_budget, mode)
            print(f"Mode: {mode.capitalize()}, Budget: Rs. {max_budget}")
            print(f"Spent: Rs. {spent:.2f}, Remaining: Rs. {left:.2f}")
        elif opt == '6':
            print(f"Goodbye, {user}!")
            break
        else:
            print("Please choose a valid option.")
def record_expense(log):
    date_str = input("Date (YYYY-MM-DD): ")
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except:
        print("Bad date format.")
        return
    print("Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"{i}. {cat}")
    try:
        cat_idx = int(input("Select category #: "))
        category = CATEGORIES[cat_idx - 1] if 1 <= cat_idx <= len(CATEGORIES) else "Other"
        amount = float(input(f"Amount for {category}: "))
        if amount < 0:
            print("Negative amount not allowed.")
            return
        log.append({'date': date_str, 'category': category, 'amount': amount})
        print("Expense recorded.")
    except:
        print("Something went wrong. Entry skipped.")
def list_expenses(log):
    if not log:
        print("No expenses yet.")
        return
    for i, row in enumerate(log, 1):
        print(f"{i}. {row['date']} | {row['category']} | Rs. {row['amount']}")
def modify_entry(log):
    list_expenses(log)
    try:
        index = int(input("Which entry to update? (0 to cancel): ")) - 1
        if index == -1:
            return
        if 0 <= index < len(log):
            new_date = input("New date (or blank to keep): ")
            if new_date:
                try:
                    datetime.strptime(new_date, "%Y-%m-%d")
                    log[index]['date'] = new_date
                except:
                    print("Invalid date. Keeping current.")
            print(f"Current Category: {log[index]['category']}")
            if input("Change category? [y/n]: ").lower() == 'y':
                for i, cat in enumerate(CATEGORIES, 1):
                    print(f"{i}. {cat}")
                try:
                    new_cat = int(input("Pick category #: "))
                    if 1 <= new_cat <= len(CATEGORIES):
                        log[index]['category'] = CATEGORIES[new_cat - 1]
                except:
                    print("Invalid selection.")
            amt_input = input("New amount (blank to skip): ")
            if amt_input:
                try:
                    new_amt = float(amt_input)
                    if new_amt >= 0:
                        log[index]['amount'] = new_amt
                except:
                    print("Invalid value. Skipping amount update.")
            print("Update complete.")
        else:
            print("Bad index.")
    except:
        print("Invalid input.")
def remove_expense(log):
    list_expenses(log)
    try:
        index = int(input("Entry to delete (0 to cancel): ")) - 1
        if index == -1:
            return
        confirm = input(f"Delete item {index+1}? [y/n]: ").lower()
        if confirm == 'y':
            del log[index]
            print("Deleted.")
    except:
        print("Invalid choice.")
def store_expenses(user, data):
    fname = f"{EXP_PREFIX}{user}.csv"
    with open(fname, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'category', 'amount'])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
def budget_setup():
    print("\nPick budget cycle:")
    print("1. Weekly")
    print("2. Monthly")
    while True:
        choice = input("1 or 2: ").strip()
        if choice in ('1', '2'):
            mode = 'weekly' if choice == '1' else 'monthly'
            break
        print("Please type 1 or 2.")
    while True:
        try:
            amt = float(input(f"Budget for {mode}: Rs. "))
            if amt >= 0:
                return mode, amt
        except:
            pass
        print("Try a valid positive number.")
def get_remaining_budget(log, budget, mode):
    today = datetime.now()
    if mode == 'weekly':
        start = today - timedelta(days=today.weekday())
        spent = sum(e['amount'] for e in log if datetime.strptime(e['date'], "%Y-%m-%d") >= start)
    else:
        spent = sum(e['amount'] for e in log if datetime.strptime(e['date'], "%Y-%m-%d").month == today.month)
    return budget - spent, spent
if __name__ == "__main__":
    load_admin_config()
    login_flow()
