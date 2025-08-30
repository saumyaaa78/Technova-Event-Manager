import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from tkcalendar import Calendar
import datetime
import os
import hashlib

# Load club schedules from a file if it exists, otherwise initialize as an empty dictionary
club_schedules_file = "club_schedules.json"

if os.path.exists(club_schedules_file):
    with open(club_schedules_file, "r") as file:
        club_schedules = json.load(file)
else:
    club_schedules = {}
    messagebox.showinfo("File Not Found", "Club schedules file not found. It will be created as an empty file.")

# President password
president_password = "123"  # password

# Global variable to track whether the president is logged in
president_logged_in = False

# Global variables for UI elements
club_menu = None
club_var = None
president_window = None
cal = None  # Calendar widget

# Define available colors for clubs
available_colors = ["#FF6347", "#4169E1", "#32CD32", "#FF8C00", "#9932CC", "#00CED1", "#FF00FF", "#FFFF00", "#FF69B4", "#A52A2A"]

def save_club_schedules():
    with open(club_schedules_file, "w") as file:
        json.dump(club_schedules, file)

def update_club_dropdown():
    global club_menu
    club_menu['menu'].delete(0, 'end')
    for club in club_schedules.keys():
        club_menu['menu'].add_command(label=club, command=tk._setit(club_var, club))

def show_schedule():
    schedule_window = tk.Toplevel(root)
    schedule_window.title("Club Meeting Schedule")
    schedule_window.geometry("600x400")  # Set window dimensions

    schedule_text = tk.Text(schedule_window, wrap="word", width=60, height=30)
    schedule_text.pack(padx=10, pady=10, fill="both", expand=True)

    for club_name, events in club_schedules.items():
        schedule_text.insert("end", f"{club_name} Schedule:\n")
        for date, event in events.items():
            schedule_text.insert("end", f"{date}: {event}\n")
        schedule_text.insert("end", "\n")

    schedule_text.config(state="disabled")

def show_all_events():
    all_events_window = tk.Toplevel(president_window)
    all_events_window.title("All Events")
    all_events_window.geometry("600x400")  # Set window dimensions

    all_events_text = tk.Text(all_events_window, wrap="word", width=60, height=30)
    all_events_text.pack(padx=10, pady=10, fill="both", expand=True)

    for club_name, events in club_schedules.items():
        all_events_text.insert("end", f"{club_name} Events:\n")
        for date, event in events.items():
            all_events_text.insert("end", f"{date}: {event}\n")
        all_events_text.insert("end", "\n")

    all_events_text.config(state="disabled")

def president_login():
    global president_logged_in
    password = simpledialog.askstring("President Login", "Enter the president password:", show='*')
    # Hash the entered password and compare with the hashed password stored
    if hashlib.sha256(password.encode()).hexdigest() == hashlib.sha256(president_password.encode()).hexdigest():
        president_logged_in = True
        messagebox.showinfo("Success", "President logged in successfully.")
        root.destroy()  # Close the main window upon successful login
        open_president_window()  # Open the president window
    else:
        messagebox.showerror("Error", "Incorrect password.")

def add_event_window():
    club_name = club_var.get()
    if club_name:
        if club_name in club_schedules:
            event_window = tk.Toplevel(president_window)
            event_window.title("Add Event")
            event_window.geometry("400x300")  # Set window dimensions

            cal = Calendar(event_window, selectmode='day', year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day, date_pattern="y-mm-dd", day_abbr_font_size=20)
            cal.pack(pady=20, fill='both', expand=True)  # Fill both vertically and horizontally

            # Mark booked dates on the calendar
            mark_booked_dates(cal)

            event_entry = tk.Entry(event_window)
            event_entry.pack(pady=5)

            def add_event_to_schedule():
                club_name = club_var.get()
                if not club_name:
                    messagebox.showerror("Error", "Please select a club.")
                    return

                date_str = cal.get_date()
                event = event_entry.get().strip()

                if not event:
                    messagebox.showerror("Error", "Please enter an event.")
                    return

                try:
                    date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()  # Convert date string to datetime.date
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                    return

                # Check if the date is already booked by another club
                for existing_club, events in club_schedules.items():
                    if date_str in events and existing_club != club_name:
                        messagebox.showerror("Error", f"The date {date_str} is already booked by '{existing_club}'.")
                        return

                # If the date is not already booked, register the event
                if date_str not in club_schedules[club_name]:
                    club_schedules[club_name][date_str] = event
                    save_club_schedules()  # Save the updated schedules
                    messagebox.showinfo("Success", "Event added successfully.")

                    # Mark the calendar with the booked event date
                    year, month, day = map(int, date_str.split("-"))
                    cal_date = datetime.date(year, month, day)
                    color = available_colors[(len(available_colors) + list(club_schedules.keys()).index(club_name)) % len(available_colors)]
                    cal.tag_config(club_name, background=color)
                    cal.calevent_create(cal_date, text=club_name, tags=club_name)
                    event_window.destroy()
                else:
                    messagebox.showerror("Error", f"An event already exists for this date by '{club_name}'.")

            add_button = tk.Button(event_window, text="Add Event", command=add_event_to_schedule)
            add_button.pack(pady=5)
        else:
            messagebox.showerror("Error", f"Club '{club_name}' not found.")
    else:
        messagebox.showerror("Error", "Please select a club.")

def add_new_club_window():
    new_club_name = simpledialog.askstring("New Club", "Enter the name of the new club:")
    if new_club_name:
        new_club_name = new_club_name.strip()
        if new_club_name:
            if new_club_name not in club_schedules:
                club_schedules[new_club_name] = {}
                save_club_schedules()  # Save the updated schedules
                messagebox.showinfo("Success", f"New club '{new_club_name}' added successfully.")
                update_club_dropdown()  # Update club dropdown with new club
            else:
                messagebox.showerror("Error", f"Club '{new_club_name}' already exists.")
        else:
            messagebox.showerror("Error", "Please enter a valid club name.")

def remove_club_window():
    selected_club = club_var.get()
    if selected_club:
        confirmation = messagebox.askokcancel("Confirm Removal", f"Are you sure you want to remove '{selected_club}' club?")
        if confirmation:
            del club_schedules[selected_club]
            save_club_schedules()  # Save the updated schedules
            update_club_dropdown()  # Update club dropdown
            messagebox.showinfo("Success", f"Club '{selected_club}' removed successfully.")
    else:
        messagebox.showerror("Error", "Please select a club to remove.")

def remove_event_window():
    club_name = club_var.get()
    if club_name:
        event_date = simpledialog.askstring("Remove Event", "Enter the date of the event to remove (YYYY-MM-DD):")
        if event_date:
            if event_date in club_schedules[club_name]:
                confirmation = messagebox.askokcancel("Confirm Removal", f"Are you sure you want to remove the event on {event_date}?")
                if confirmation:
                    del club_schedules[club_name][event_date]
                    save_club_schedules()  # Save the updated schedules
                    messagebox.showinfo("Success", "Event removed successfully.")
            else:
                messagebox.showerror("Error", "No event found on the specified date.")
        else:
            messagebox.showerror("Error", "Please enter a valid date.")
    else:
        messagebox.showerror("Error", "Please select a club.")

def add_event():
    if president_logged_in:
        add_event_window()
    else:
        messagebox.showerror("Error", "You need to login as president to add events.")

def add_new_club():
    if president_logged_in:
        add_new_club_window()
    else:
        messagebox.showerror("Error", "You need to login as president to add new clubs.")

def open_president_window():
    global club_menu
    global club_var
    global president_window
    global cal  # Calendar widget

    president_window = tk.Tk()
    president_window.title("President Options")
    president_window.geometry("800x600")  # Set initial window size

    # Calendar
    cal = Calendar(president_window, selectmode='day', year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day, date_pattern="y-mm-dd", day_abbr_font_size=20)
    cal.pack(pady=20, fill='both', expand=True)  # Fill both vertically and horizontally

    # Mark booked dates on the calendar
    mark_booked_dates(cal)

    # Club name selection
    ttk.Label(president_window, text="Select Club:").pack(pady=(10, 0))
    club_var = tk.StringVar()
    club_menu = ttk.OptionMenu(president_window, club_var, "Select Club")
    club_menu.pack(pady=5)

    update_club_dropdown()  # Initialize club dropdown

    add_event_button = ttk.Button(president_window, text="Add Event", command=add_event)
    add_event_button.pack(pady=5)

    add_club_button = ttk.Button(president_window, text="Add New Club", command=add_new_club)
    add_club_button.pack(pady=5)

    remove_club_button = ttk.Button(president_window, text="Remove Club", command=remove_club_window)
    remove_club_button.pack(pady=5)

    remove_event_button = ttk.Button(president_window, text="Remove Event", command=remove_event_window)
    remove_event_button.pack(pady=5)

    show_all_events_button = ttk.Button(president_window, text="Show All Events", command=show_all_events)
    show_all_events_button.pack(pady=5)

def mark_booked_dates(calendar):
    for club, events in club_schedules.items():
        for date_str in events.keys():
            year, month, day = map(int, date_str.split("-"))
            cal_date = datetime.date(year, month, day)
            color = available_colors[(len(available_colors) + list(club_schedules.keys()).index(club)) % len(available_colors)]
            calendar.tag_config(club, background=color)
            calendar.calevent_create(cal_date, text=club, tags=club)

# Create main window
root = tk.Tk()
root.title("Club Meeting Schedule")

# Styling
style = ttk.Style(root)
style.theme_use('clam')

root.geometry("800x600")  # Set initial window size

# Calendar
cal = Calendar(root, selectmode='day', year=datetime.datetime.now().year, month=datetime.datetime.now().month, day=datetime.datetime.now().day, date_pattern="y-mm-dd", day_abbr_font_size=20)
cal.pack(pady=20, fill='both', expand=True)  # Fill both vertically and horizontally

# Mark booked dates on the calendar
mark_booked_dates(cal)

# Buttons
show_schedule_button = ttk.Button(root, text="All Event Schedules", command=show_schedule)
show_schedule_button.pack(pady=5)

login_button = ttk.Button(root, text="Login", command=president_login)
login_button.pack(pady=5)

root.mainloop()
