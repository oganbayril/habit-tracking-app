from tkinter import *
from tkinter import messagebox
import sqlite3
import os
from datetime import date, timedelta, datetime
from collections import OrderedDict

# The name of the sqlite3 database where user's inputs will be saved in
data_saving_file = "habits.db"

DARK_MODE_COLOR = "#121212"
DEFAULT_COLOR = "SystemButtonFace"

# Activating/deactivating dark mode in our main window.
def dark_mode():
    if dark_mode_var.get() == 0:
        cursor.execute("""UPDATE habits 
                  SET dark_mode_var = :updated_dark_mode_var
                  WHERE dark_mode_var = :old_dark_mode_var""",
                  {"updated_dark_mode_var": dark_mode_var.get(), "old_dark_mode_var": 1})
        connect.commit()
        
        root.config(bg=DEFAULT_COLOR)
        frame.config(bg=DEFAULT_COLOR, fg="black")
        habits_listbox.config(bg=DEFAULT_COLOR, fg="black")
        
        button_frame.config(bg=DEFAULT_COLOR)
        add_button.config(bg=DEFAULT_COLOR, fg="black", activebackground=DEFAULT_COLOR, activeforeground="black")
        remove_button.config(bg=DEFAULT_COLOR, fg="black", activebackground=DEFAULT_COLOR, activeforeground="black")
        update_button.config(bg=DEFAULT_COLOR, fg="black", activebackground=DEFAULT_COLOR, activeforeground="black")
        progress_button.config(bg=DEFAULT_COLOR, fg="black", activebackground=DEFAULT_COLOR, activeforeground="black")
        dark_mode_button.config(bg=DEFAULT_COLOR, fg="black", activebackground=DEFAULT_COLOR, activeforeground="black", selectcolor="white")
        
    else:
        cursor.execute("""UPDATE habits 
                  SET dark_mode_var = :updated_dark_mode_var
                  WHERE dark_mode_var = :old_dark_mode_var""",
                  {"updated_dark_mode_var": dark_mode_var.get(), "old_dark_mode_var": 0})

        connect.commit()

        root.config(bg=DARK_MODE_COLOR)
        frame.config(bg=DARK_MODE_COLOR, fg="white")
        habits_listbox.config(bg=DARK_MODE_COLOR, fg="white")

        button_frame.config(bg=DARK_MODE_COLOR)
        add_button.config(bg=DARK_MODE_COLOR, fg="white", activebackground=DARK_MODE_COLOR, activeforeground="white")
        remove_button.config(bg=DARK_MODE_COLOR, fg="white", activebackground=DARK_MODE_COLOR, activeforeground="white")
        update_button.config(bg=DARK_MODE_COLOR, fg="white", activebackground=DARK_MODE_COLOR, activeforeground="white")
        progress_button.config(bg=DARK_MODE_COLOR, fg="white", activebackground=DARK_MODE_COLOR, activeforeground="white")
        dark_mode_button.config(bg=DARK_MODE_COLOR, fg="white", activebackground=DARK_MODE_COLOR, activeforeground="white", selectcolor=DARK_MODE_COLOR)

# Function which makes the user toggle the completion of the habit when user clicks on a habit in the listbox
# Only changes the completion of the day the program was run in
def toggle():
    if len(habits) == 0:
        messagebox.showinfo("No habits", "Please add a habit first.")
        return
    
    habit_index = habits_listbox.curselection()[0]
    habit = list(habits)[habit_index]
    completion = list(habits[habit])[1]
    if completion == "☐":
        completion = "☑"
    elif completion == "☑":
        completion = "☒"
    else:
        completion = "☐"
    
    changing_checkbox = list(habits[habit])
    changing_checkbox[1] = completion
    habits[habit] = tuple(changing_checkbox)
    
    cursor.execute("""UPDATE habits 
                  SET completion = :completion 
                  WHERE habit = :habit 
                  AND date = :date"""
                  , {"completion": completion, "habit": habit, "date": str(today)})

    connect.commit()
    
    habits_listbox.delete(habit_index)
    habits_listbox.insert(habit_index, habits[habit][1]+habit)
    
    
# Resetting every button state
def reset_button(event=None):
    add_button["relief"] = RAISED
    remove_button["relief"] = RAISED
    update_button["relief"] = RAISED
    progress_button["relief"] = RAISED
    
    add_button.config(state=NORMAL)
    remove_button.config(state=NORMAL)
    update_button.config(state=NORMAL, padx=23)
    progress_button.config(state=NORMAL)
    habits_listbox.config(state=NORMAL)
    dark_mode_button.config(state=NORMAL)
    
    remove_button["text"] = "Remove a habit"
    update_button["text"] = "Update a habit"
    habits_listbox.bind("<<ListboxSelect>>", lambda event: toggle())

# Limiting the lenght of each habit when they're getting created so the user can't make an infinitely long input which may cause trouble for the code
def limiting_habit_lenght(habit_name):
    if len(habit_name) <= 25:
        return True
    else:
        return False

# Adding new habits to the dictionary, the listbox and the database
def adding(event=None):
    global habits
    habit_name = entry.get()
    
    if len(habit_name) == 0:
        return
    
    if habit_name not in habits and habit_name not in habits_to_remove:
        habits[habit_name] = (str(today), "☐")
        habits_listbox.delete(0, END)
        cursor.execute("INSERT INTO habits VALUES (:habit, :date, :completion, :dark_mode_var)"
                       , {"habit": habit_name, "date": str(today), "completion": habits[habit_name][1], "dark_mode_var": dark_mode_var.get()})
        connect.commit()
        
        for j, habit in enumerate(habits):
            habits_listbox.insert(j, habits[habit][1]+habit)
    else:
        messagebox.showinfo("Info", "Habit already exists")
    
    top.destroy()

# Creating the window which'll be used to get the input from the user to add new habits
def add_habit():
    global top, entry
    add_button.config(state=DISABLED)
    remove_button.config(state=DISABLED)
    update_button.config(state=DISABLED)
    progress_button.config(state=DISABLED)
    dark_mode_button.config(state=DISABLED)
    add_button["relief"] = SUNKEN
    top = Toplevel()
    top.title("Add a habit")
    
    add_label = Label(top, text="Name of the habit you want to add:", font="Georgia")
    entry = Entry(top, width=20, validate="key", validatecommand=validate, font="Georgia")
    adding_button = Button(top, text="Add", command=adding, font="Georgia")
    
    if dark_mode_var.get() == 1:
        top.config(bg=DARK_MODE_COLOR)
        add_label.config(bg=DARK_MODE_COLOR, fg="white")
        adding_button.config(bg=DARK_MODE_COLOR, fg="white", activebackground=DARK_MODE_COLOR, activeforeground="white")
    
    add_label.grid(row=0)
    entry.grid(row=1)
    adding_button.grid(row=2)
    entry.focus()
    top.bind("<Return>", adding)
    top.bind("<Destroy>", reset_button)

# Removing an existing habit from the dictionary, listbox and the database
def removing():
    habit_index = habits_listbox.curselection()[0]
    habit = list(habits)[habit_index]
    confirm = messagebox.askyesno("Are you sure?", f"Do you want to remove {habit}?")
    
    if confirm is True:
        habits.pop(habit)
        habits_listbox.delete(habit_index)
        cursor.execute("DELETE from habits where habit = :habit",
                        {"habit": habit})
        connect.commit()
    elif confirm is False:
        reset_button()
        return
    reset_button()

# Allows the user to remove an existing habit which they can do by selecting a habit in the listbox
def remove_habit():
    global habits, habits_listbox
    if len(habits) == 0:
        messagebox.showinfo("No habits", "There are no habits to remove.")
        reset_button()
        return
    remove_button.config(state=DISABLED)
    remove_button["text"] = "Select the habit"
    remove_button["relief"] = SUNKEN
    habits_listbox.bind("<<ListboxSelect>>", lambda event: removing())

# Updating habit's name in the dictionary, listbox and the database
def updating_habit_name():
    global habits
    updated_habit_name = updating_entry.get()
    
    if updated_habit_name in habits:
        messagebox.showerror("Error", "Habit already exists.")
        updating_top.destroy()
        reset_button()
        return
    
    cursor.execute("""UPDATE habits 
                  SET habit = :updated_habit
                  WHERE habit = :old_habit""",
                  {"updated_habit": updated_habit_name, "old_habit": habit})

    connect.commit()
    
    reset_button()
    
    # Updating the dictionary 
    updated_habits = OrderedDict((updated_habit_name if key == habit else key, value) for key, value in habits.items())
    habits = updated_habits
    
    habits_listbox.delete(habit_index)
    habits_listbox.insert(habit_index, habits[updated_habit_name][1]+updated_habit_name)
    updating_top.destroy()

# New window for the update proccess
def updating(event):
    global updating_entry, habit_index, habit, updating_top
    add_button.config(state=DISABLED)
    remove_button.config(state=DISABLED)
    progress_button.config(state=DISABLED)
    dark_mode_button.config(state=DISABLED)
    habits_listbox.config(state=DISABLED)

    selected_indices = habits_listbox.curselection()
    if not selected_indices:
        return

    habit_index = selected_indices[0]
    habit = list(habits)[habit_index]

    updating_top = Toplevel()
    updating_top.title(f"Updating {habit}")
    updating_name_label = Label(updating_top, text="Update the name to your liking:", font="Georgia")
    updating_entry = Entry(updating_top, font="Georgia")
    updating_button = Button(updating_top, text="Update", font="Georgia", command=updating_habit_name)
    
    if dark_mode_var.get() == 1:
        updating_top.config(bg=DARK_MODE_COLOR)
        updating_name_label.config(bg=DARK_MODE_COLOR, fg="white")
        updating_button.config(bg=DARK_MODE_COLOR, fg="white", activebackground=DARK_MODE_COLOR, activeforeground="white")
    
    updating_entry.insert(0, habit)
    updating_entry.focus()
    updating_top.bind("<Return>", lambda event: updating_habit_name())
    updating_top.bind("<Destroy>", reset_button)

    updating_name_label.grid(row=0)
    updating_entry.grid(row=1)
    updating_button.grid(row=2)


# Allows the user to update an existing habit which they can do by selecting a habit in the listbox
def update_habit():
    global habits, habits_listbox
    if len(habits) == 0:
        messagebox.showinfo("No habits", "There are no habits to update.")
        reset_button()
        return
    update_button.config(state=DISABLED, padx=20)
    update_button["text"] = "Select the habit"
    update_button["relief"] = SUNKEN
    
    habits_listbox.bind("<<ListboxSelect>>", updating)
    

# Function which allows the user to toggle completion of each habit when user clicks on it
# Can change the completion of the whole week and only doable on the progress screen window
def progress_screen_toggle(event, completion, index):
    if completion["text"] == "☐":
        completion["text"] = "☑"
        completion.config(fg="green")
        
    elif completion["text"] == "☑":
        completion["text"] = "☒"
        completion.config(fg="red")
        
    else:
        completion["text"] = "☐"
        completion.config(fg="blue")
    
    completion = str(completion.cget("text"))
        
    cursor.execute("""UPDATE habits 
                  SET completion = :completion
                  WHERE habit = :habit
                  AND date = :date
                  """
                  , {"completion": completion, "habit": fetch[index][0], "date": fetch[index][1]})

    connect.commit()
    
    updated_data = cursor.execute("SELECT habit, date, completion FROM habits")
    updated_fetch = updated_data.fetchall()
    
    for i, habit in enumerate(habits):
        completed = 0
        total = 0
        
        for j in range(len(updated_fetch)):
            checking_days = datetime.strptime(updated_fetch[j][1], "%Y-%m-%d").date()
            if days[-1] < checking_days:
                continue
            else:
                if updated_fetch[j][0] == habit and updated_fetch[j][2] == "☑":
                    completed += 1
                    total += 1
                if updated_fetch[j][0] == habit and (updated_fetch[j][2] == "☐" or updated_fetch[j][2] == "☒"):
                    total += 1
                
        if updated_fetch[index][0] == habit and updated_fetch[index][1] == str(today):
            habits[habit] = (str(today), completion)
            habits_listbox.configure(state=NORMAL)
            habits_listbox.delete(i)
            habits_listbox.insert(i, habits[habit][1]+habit)
            habits_listbox.configure(state=DISABLED)
    
        percentage = int((completed/total)*100)
        percentage_label_list[i].configure(text=str(percentage)+"%")
        
# The screen which allows the user to see their progress on each habit for the past week
def progress_screen():
    global fetch, percentage_label_list, days
    
    percentage_label_list = []
    
    habits_listbox.configure(state=DISABLED)
    
    progress_button["relief"] = SUNKEN
    add_button.config(state=DISABLED)
    remove_button.config(state=DISABLED)
    update_button.config(state=DISABLED)
    progress_button.config(state=DISABLED)
    dark_mode_button.config(state=DISABLED)
    
    # Allows the user to scroll when there are lots of habits and they make up more than the window
    def scroll(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    if len(habits) == 0:
        messagebox.showinfo("Habit not found.","You need to add a habit first.")
        reset_button()
        return
    
    progress_top = Toplevel()
    progress_top.title("Progress")
    progress_top.geometry("600x400")
    progress_top.focus()
    
    canvas = Canvas(progress_top, bg=DEFAULT_COLOR)
    scrollbar = Scrollbar(progress_top, orient=VERTICAL, command=canvas.yview)
    frame = Frame(canvas, bg=DEFAULT_COLOR)
    
    canvas.pack(side=LEFT, fill="both", expand=True)
    scrollbar.pack(side=LEFT, fill="y")
    canvas.create_window((0, 0), window=frame, anchor=NW)
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind_all("<MouseWheel>", scroll)
    
    days = []
    
    data = cursor.execute("SELECT habit, date, completion FROM habits")
    fetch = data.fetchall()
    
    for i in range(7):
        day = today - timedelta(days=i)
        days.insert(0, day)
   
            
    for i, habit in enumerate(habits):
        progress_labelframe = LabelFrame(frame)
        progress_labelframe.grid(row=i, sticky="nesw")
        habit_label = Label(progress_labelframe, text=habit, font=("Georgia", 14))
        habit_label.grid(row=0, column=0, sticky="w", padx=10, columnspan=7)
        
        completed = 0
        total = 0
        
        for j in range(7):
            each_day_labelframe = LabelFrame(progress_labelframe)
            each_day_labelframe.grid(row=1, column=j, sticky="nesw")
            
            day_names_text = days[j].strftime("%a")
            day_numbers_text = days[j].strftime("%d")
            days_str = str(days[j])
            
            day_names_label = Label(each_day_labelframe, text=day_names_text, font="Georgia", width=6)
            day_numbers_label = Label(each_day_labelframe, text=day_numbers_text, font="Georgia", width=6)
            
            if dark_mode_var.get() == 1:
                each_day_labelframe.config(bg=DARK_MODE_COLOR)
                day_names_label.config(bg=DARK_MODE_COLOR, fg="white")
                day_numbers_label.config(bg=DARK_MODE_COLOR, fg="white")
            
            day_names_label.grid(row=0, column=j, sticky="we", ipadx=2)
            day_numbers_label.grid(row=1, column=j, sticky="we", ipadx=2)
        
            for k in range(len(fetch)):
                checking_days = datetime.strptime(fetch[k][1], "%Y-%m-%d").date()
                if days[-1] < checking_days:
                    continue
                else:
                    if fetch[k][0] == habit and fetch[k][2] == "☑":
                        completed += 1
                        total += 1
                    elif fetch[k][0] == habit and (fetch[k][2] == "☐" or fetch[k][2] == "☒"):
                        total += 1
                
                if fetch[k][0] == habit and fetch[k][1] == days_str:
                    completions = Label(each_day_labelframe, text=fetch[k][2], font=("Georgia", 20))
                    completions.grid(row=2, column=j, sticky="we", ipadx=15)
                    if fetch[k][2] == "☑":
                        completions.config(fg="green")
                    elif fetch[k][2] == "☒":
                        completions.config(fg="red")
                    else:
                        completions.config(fg="blue")
                    
                    if dark_mode_var.get() == 1:
                        completions.config(bg=DARK_MODE_COLOR)
                    
                    # Letting the user change completion of any habit for the week, intended to help the user change completion if they haven't run the code in a few days
                    completions.bind("<Button-1>", lambda event, toggle=completions, index=k: progress_screen_toggle(event, toggle, index))
            
        percentage = int((completed/total)*100)
        percentage_label = Label(progress_labelframe, text=str(percentage)+"%", font=("Georgia", 10))
        percentage_label.grid(row=3, sticky="w", ipadx=5, columnspan=2)
        percentage_label_list.append(percentage_label)
        
        if dark_mode_var.get() == 1:
            canvas.config(bg=DARK_MODE_COLOR)
            progress_labelframe.config(bg=DARK_MODE_COLOR)
            habit_label.config(bg=DARK_MODE_COLOR, fg="white")
            percentage_label.config(bg=DARK_MODE_COLOR, fg="white")
    
    frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    progress_top.bind("<Destroy>", reset_button)
    



today = date.today()

root = Tk()
root.title("Habit tracking app")
root.geometry("900x600")

# Things that go to the left of the screen
frame = LabelFrame(root, text="Today", font="Georgia", padx=10, pady=2)
habits_listbox = Listbox(frame, selectmode=SINGLE, width=25, font=("Georgia", 14), bg=DEFAULT_COLOR)
habits_listbox_scrollbar = Scrollbar(frame, orient="vertical", command=habits_listbox.yview)

frame.grid(row=0, column=0, rowspan=3, sticky="nesw", padx=10)
habits_listbox.pack(side=LEFT, fill="y" ,expand=True)
habits_listbox.config(yscrollcommand=habits_listbox_scrollbar.set)
habits_listbox_scrollbar.pack(side=RIGHT, fill="y", expand=True)

habits_listbox.bind("<<ListboxSelect>>", lambda event: toggle())
validate = (root.register(limiting_habit_lenght), "%P")

# Things that go to the right of the screen
button_frame = LabelFrame(root, padx=10, pady=10)
add_button = Button(button_frame, text="Add a habit", padx=35, pady=5, command=add_habit, font="Georgia")
remove_button = Button(button_frame, text="Remove a habit", padx=20, pady=5, command=remove_habit, font="Georgia") 
update_button = Button(button_frame, text="Update a habit", padx=23, pady=5, command=update_habit, font="Georgia")
progress_button = Button(button_frame, text="Progress", padx=44, pady=5, command=progress_screen, font="Georgia" )

button_frame.grid(row=0, column=3, rowspan=1, sticky="ne")
add_button.pack()
remove_button.pack()
update_button.pack()
progress_button.pack()

root.grid_columnconfigure(0, weight=0)
root.grid_columnconfigure(1, weight=2)
root.grid_columnconfigure(2, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)

# Getting the data if a table exists
if os.path.exists(data_saving_file):
    connect = sqlite3.connect(data_saving_file)
    cursor = connect.cursor()
    
    getting_dark_mode_var = cursor.execute("SELECT dark_mode_var FROM habits")
    fetching_dark_mode_var = getting_dark_mode_var.fetchone()
    
    if fetching_dark_mode_var != None:
        dark_mode_var = IntVar(value=fetching_dark_mode_var[0])
    else:
        dark_mode_var = IntVar()
    
    dark_mode_button = Checkbutton(button_frame, text="Dark mode", variable=dark_mode_var, font=("Georgia", 12), command=dark_mode)
    dark_mode_button.pack()
    
    if dark_mode_var.get() == 1:
        dark_mode_button.select()
        dark_mode()
    
    habits = OrderedDict()
    habits_to_remove = []
    
    getting_data = cursor.execute("SELECT habit, date, completion FROM habits")
    fetching_data = getting_data.fetchall()
    
    # Organising the "habits" dictionary where each key: value pair will be "habit: (date, completion)"
    for i in range(len(fetching_data)):
        organising_data_keys = fetching_data[i][0]
        organising_data_values = fetching_data[i][1:]
        habits[organising_data_keys] = (organising_data_values)
    
    for j, habit in enumerate(habits):
        latest_run_day = habits[habit][0]
        last_run_day_datetime = datetime.strptime(latest_run_day, "%Y-%m-%d").date()
        day_difference = (today-last_run_day_datetime).days
        
        # If last time the code ran was day/days before today, we add every missing day to the database and we insert each habit into our listbox where the date will be today
        if day_difference > 0:
            for k in range((day_difference-1), -1, -1):
                habits[habit] = (str(today-timedelta(days=k)), "☐")
                cursor.execute("INSERT INTO habits VALUES (:habit, :date, :completion, :dark_mode_var)"
                               , {"habit": habit, "date": habits[habit][0], "completion": habits[habit][1], "dark_mode_var": dark_mode_var.get()})
                connect.commit() 
            
            habits[habit] = (str(today), "☐")
            habits_listbox.insert(j, habits[habit][1]+habit)
        
        # If code was already ran today, no data changes, so we just insert our habits and the completions in our listbox
        # If user changes the date of their computer to be a previous day, if the habit used to exist in that date it gets inserted to the listbox, if not it gets deleted from the dictionary
        else:
            counter = 0
            for l in range(len(fetching_data)):
                if fetching_data[l][0] == habit and fetching_data[l][1] == str(today):
                    habits[habit] = (str(today), fetching_data[l][2])
                    counter += 1
            if counter == 0:
                habits_to_remove.append(habit)       
            else:
                habits_listbox.insert(j, habits[habit][1]+habit)
    
    for element in habits_to_remove:
        habits.pop(element)

# Creating a database if it doesn't exist
else:
    connect = sqlite3.connect(data_saving_file)
    cursor = connect.cursor()   
    cursor.execute("""CREATE TABLE habits (
                    habit text,
                    date text,
                    completion text,
                    dark_mode_var integer NULL
                    )""")
    connect.commit()
    habits = OrderedDict()
    habits_to_remove = []
    dark_mode_var = IntVar()
    dark_mode_button = Checkbutton(button_frame, text="Dark mode", variable=dark_mode_var, font=("Georgia", 12), command=dark_mode)
    dark_mode_button.pack()

root.mainloop()