import subprocess
import tkinter as tk
from tkinter import messagebox
import psutil
from tkinter import ttk
from ttkthemes import ThemedStyle

def add_task():
    task = task_entry.get()
    if task:
        tasks.append(task)
        task_list.insert(tk.END, task)
        task_entry.delete(0, tk.END)
        messagebox.showinfo("Task Manager", "Task added successfully.")
    else:
        messagebox.showwarning("Task Manager", "Please enter a task.")

def remove_task():
    selected_indices = task_list.curselection()
    if selected_indices:
        task_index = selected_indices[0]
        task = tasks.pop(task_index)
        task_list.delete(task_index)
        messagebox.showinfo("Task Manager", f"Task '{task}' removed successfully.")
    else:
        messagebox.showwarning("Task Manager", "Please select a task.")

def kill_process():
    selected_indices = task_list.curselection()
    if selected_indices:
        task_index = selected_indices[0]
        task = tasks[task_index]
        process_id = process_ids[task_index]
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(process_id)], check=True)
            tasks.pop(task_index)
            process_ids.pop(task_index)
            task_list.delete(task_index)
            messagebox.showinfo("Task Manager", f"Process {process_id} killed successfully.")
        except subprocess.CalledProcessError:
            messagebox.showerror("Task Manager", f"Failed to kill process {process_id}.")
    else:
        messagebox.showwarning("Task Manager", "Please select a task.")

def view_subprocesses():
    selected_indices = task_list.curselection()
    if selected_indices:
        task_index = selected_indices[0]
        task = tasks[task_index]
        process_id = process_ids[task_index]
        try:
            output = subprocess.check_output(["tasklist", "/FI", f"PID eq {process_id}"]).decode()
            messagebox.showinfo("Subprocesses", f"Subprocesses for Process {process_id}:\n\n{output}")
        except subprocess.CalledProcessError:
            messagebox.showerror("Task Manager", f"Failed to retrieve subprocesses for process {process_id}.")
    else:
        messagebox.showwarning("Task Manager", "Please select a task.")

def view_process_details():
    selected_indices = task_list.curselection()
    if selected_indices:
        task_index = selected_indices[0]
        task = tasks[task_index]
        process_id = process_ids[task_index]
        try:
            process = psutil.Process(process_id)
            process_details = f"Process ID: {process.pid}\n" \
                              f"Name: {process.name()}\n" \
                              f"Status: {process.status()}\n" \
                              f"Username: {process.username()}\n" \
                              f"Memory Info: {process.memory_info()}\n" \
                              f"CPU Percent: {process.cpu_percent(interval=0.1)}%"
            messagebox.showinfo("Process Details", process_details)
        except psutil.NoSuchProcess:
            messagebox.showerror("Task Manager", f"Failed to retrieve details for process {process_id}.")

def show_context_menu(event):
    selected_indices = task_list.curselection()
    if selected_indices:
        context_menu.post(event.x_root, event.y_root)

def save_options():
    dark_mode_state = dark_mode_var.get()

    try:
        with open("options.txt", "w") as file:
            file.write(f"Dark Mode: {dark_mode_state}\n")
        messagebox.showinfo("Options", "Options saved successfully.")

        toggle_dark_mode()
    except OSError:
        messagebox.showerror("Options", "Failed to save options.")

def load_options():
    try:
        with open("options.txt", "r") as file:
            for line in file:
                if line.startswith("Dark Mode:"):
                    dark_mode_state = int(line.split(":")[1].strip())
                    dark_mode_var.set(dark_mode_state)
                    toggle_dark_mode()
                    break
    except OSError:
        messagebox.showerror("Options", "Failed to load options.")

def configure_task_list():
    task_list.configure(background=style.lookup("TFrame", "background"), foreground=style.lookup("TFrame", "foreground"))
def toggle_dark_mode():
    if dark_mode_var.get() == 1:
        style.theme_use("equilux")
    else:
        style.theme_use("arc")

    configure_task_list()

window = tk.Tk()
window.title("Python Task Manager - Made by anormalpersonsalt")

style = ThemedStyle(window)
style.set_theme("arc")

style.configure("TListbox", background=style.lookup("TFrame", "background"))
style.configure("TButton", relief=tk.FLAT)

tab_control = ttk.Notebook(window)

tasks_tab = ttk.Frame(tab_control)
tab_control.add(tasks_tab, text="Tasks")

task_frame = ttk.Frame(tasks_tab)
task_frame.pack()

task_list = tk.Listbox(task_frame, selectmode=tk.SINGLE)
task_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(task_frame, orient=tk.VERTICAL, command=task_list.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
task_list.config(yscrollcommand=scrollbar.set)

context_menu = tk.Menu(window, tearoff=0)
context_menu.add_command(label="Kill Process", command=kill_process)
context_menu.add_command(label="View Subprocesses", command=view_subprocesses)
context_menu.add_separator()
context_menu.add_command(label="View Process Details", command=view_process_details)

task_list.bind("<Button-3>", show_context_menu)

task_entry = ttk.Entry(tasks_tab)
task_entry.pack(pady=5)

button_frame = ttk.Frame(tasks_tab)
button_frame.pack(pady=5)

add_button = ttk.Button(button_frame, text="Add Task", command=add_task)
add_button.pack(side=tk.LEFT, padx=5)

remove_button = ttk.Button(button_frame, text="Remove Task", command=remove_task)
remove_button.pack(side=tk.LEFT, padx=5)

tasks = []
process_ids = []

for proc in psutil.process_iter(['pid', 'name', 'username']):
    process_id = proc.info['pid']
    process_name = proc.info['name']
    tasks.append(process_name)
    process_ids.append(process_id)
    task_list.insert(tk.END, process_name)
    if proc.info['username'] is None:
        print(f"[HIDDEN] {process_id}: {process_name}")
    else:
        print(f"{process_id}: {process_name}")

options_tab = ttk.Frame(tab_control)
tab_control.add(options_tab, text="Options")

options_frame = ttk.Frame(options_tab)
options_frame.pack()

options_label = ttk.Label(options_frame, text="Options")
options_label.pack()

dark_mode_var = tk.IntVar(value=0)
dark_mode_checkbox = ttk.Checkbutton(options_frame, text="Dark Mode", variable=dark_mode_var, command=toggle_dark_mode)
dark_mode_checkbox.pack()

save_button = ttk.Button(options_frame, text="Save", command=save_options)
save_button.pack(pady=5)

tab_control.pack(expand=True, fill=tk.BOTH)

load_options()

window.mainloop()
