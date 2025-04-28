import tkinter as tk
from tkinter import ttk, messagebox as mess, simpledialog as tsd
from PIL import Image
import cv2, os, csv, numpy as np, pandas as pd
import datetime, time, smtplib, hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Constants
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#34495e"
ACCENT_COLOR = "#3498db"
SUCCESS_COLOR = "#27ae60"
WARNING_COLOR = "#e74c3c"
TEXT_COLOR = "#ecf0f1"
TEXT_COLOR_DARK = "#2c3e50"
BG_COLOR = "#f8f9fa"
ENTRY_BG = "#ffffff"
FRAME_COLOR = "#dfe6e9"
DISABLED_COLOR = "#95a5a6"

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 12
BTN_FONT = (FONT_FAMILY, FONT_SIZE, "bold")
HEADER_FONT = (FONT_FAMILY, 20, "bold")
SUBHEADER_FONT = (FONT_FAMILY, 16, "bold")

ADMIN_ROLE = "admin"
STUDENT_ROLE = "student"
TEMP_PASSWORD = "admin123"

DEPARTMENTS = ["Computer Science", "Electrical", "Mechanical", "Civil", 
              "Electronics and Communication", "Information Technology"]
BRANCHES = ["Engineering", "Science", "Arts", "Commerce", "Management"]
PROGRAMS = ["B.Tech", "M.Tech", "B.Sc", "M.Sc", "BBA", "MBA"]

PASSWORD_SALT = "face_attendance_system_salt"
MIN_PASSWORD_LENGTH = 6

# Core Functions
def assure_path_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def hash_password(password):
    return hashlib.sha256((password + PASSWORD_SALT).encode()).hexdigest()

def create_admin_account():
    assure_path_exists("AdminDetails/")
    admin_file = "AdminDetails/admin_info.txt"
    if not os.path.isfile(admin_file):
        with open(admin_file, "w") as f:
            f.write(f"admin,{hash_password(TEMP_PASSWORD)},admin@system.com")

def check_admin_credentials(username, password):
    admin_file = "AdminDetails/admin_info.txt"
    if os.path.isfile(admin_file):
        with open(admin_file, "r") as f:
            data = f.read().strip().split(',')
            return len(data) >= 2 and username == data[0] and hash_password(password) == data[1]
    return False

def create_student_password(student_id):
    password_file = f"StudentDetails/{student_id}_psd.txt"
    if not os.path.isfile(password_file):
        default_pwd = (student_id[:6] + "123").lower()
        with open(password_file, "w") as f:
            f.write(hash_password(default_pwd))
        mess.showinfo("Student Account Created", 
                    f"Username: {student_id}\nPassword: {default_pwd}\n\nPlease change your password after first login.")
        return default_pwd
    return None

def check_student_credentials(student_id, password):
    if not os.path.isfile("StudentDetails/StudentDetails.csv"):
        return False
        
    with open("StudentDetails/StudentDetails.csv", 'r') as csvFile:
        if not any(len(row) > 2 and row[2].strip() == student_id for row in csv.reader(csvFile)):
            return False
    
    password_file = f"StudentDetails/{student_id}_psd.txt"
    if os.path.isfile(password_file):
        with open(password_file, 'r') as f:
            return f.read().strip() == hash_password(password)
    return False

def change_password():
    if hasattr(window, 'current_role'):
        if window.current_role == ADMIN_ROLE:
            change_admin_password()
        elif hasattr(window, 'current_student_id'):
            change_student_password(window.current_student_id)
    else:
        mess.showerror("Error", "No user logged in!")

def change_admin_password():
    admin_file = "AdminDetails/admin_info.txt"
    if not os.path.isfile(admin_file):
        mess.showerror("Error", "Admin account not found!")
        return
    
    with open(admin_file, "r") as f:
        admin_data = f.read().strip().split(',')
    
    change_pass_window = create_password_change_window("Change Admin Password")
    
    def save_new_password():
        current = change_pass_window.current_pass.get().strip()
        new_p = change_pass_window.new_pass.get().strip()
        confirm_p = change_pass_window.confirm_pass.get().strip()
        
        if not all([current, new_p, confirm_p]):
            change_pass_window.status_label.config(text="All fields are required!")
            return
        
        if len(new_p) < MIN_PASSWORD_LENGTH:
            change_pass_window.status_label.config(text=f"Password must be at least {MIN_PASSWORD_LENGTH} characters!")
            return
        
        if new_p != confirm_p:
            change_pass_window.status_label.config(text="New passwords don't match!")
            return
        
        if hash_password(current) != admin_data[1]:
            change_pass_window.status_label.config(text="Current password is incorrect!")
            return
        
        admin_data[1] = hash_password(new_p)
        with open(admin_file, "w") as f:
            f.write(','.join(admin_data))
        
        mess.showinfo("Success", "Admin password changed successfully!")
        change_pass_window.destroy()

    change_pass_window.save_btn.config(command=save_new_password)

def change_student_password(student_id):
    password_file = f"StudentDetails/{student_id}_psd.txt"
    if not os.path.isfile(password_file):
        mess.showerror("Error", "Student account not found!")
        return
    
    with open(password_file, "r") as f:
        stored_hash = f.read().strip()
    
    change_pass_window = create_password_change_window("Change Password")
    
    def save_new_password():
        current = change_pass_window.current_pass.get().strip()
        new_p = change_pass_window.new_pass.get().strip()
        confirm_p = change_pass_window.confirm_pass.get().strip()
        
        if not all([current, new_p, confirm_p]):
            change_pass_window.status_label.config(text="All fields are required!")
            return
        
        if len(new_p) < MIN_PASSWORD_LENGTH:
            change_pass_window.status_label.config(text=f"Password must be at least {MIN_PASSWORD_LENGTH} characters!")
            return
        
        if new_p != confirm_p:
            change_pass_window.status_label.config(text="New passwords don't match!")
            return
        
        if hash_password(current) != stored_hash:
            change_pass_window.status_label.config(text="Current password is incorrect!")
            return
        
        with open(password_file, "w") as f:
            f.write(hash_password(new_p))
        
        mess.showinfo("Success", "Password changed successfully!")
        change_pass_window.destroy()

    change_pass_window.save_btn.config(command=save_new_password)

def create_password_change_window(title):
    win = tk.Toplevel()
    win.title(title)
    win.geometry("400x250")
    win.resizable(False, False)
    win.configure(bg=BG_COLOR)
    
    style = ttk.Style()
    style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR_DARK, font=BTN_FONT)
    style.configure('TEntry', font=BTN_FONT, fieldbackground=ENTRY_BG, foreground=TEXT_COLOR_DARK)
    style.configure('TButton', font=BTN_FONT)
    
    ttk.Label(win, text=title, font=SUBHEADER_FONT, foreground=PRIMARY_COLOR).pack(pady=10)
    
    frame = ttk.Frame(win)
    frame.pack(pady=10, padx=20, fill='x')
    
    ttk.Label(frame, text="Current Password:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    win.current_pass = ttk.Entry(frame, width=25, show='*')
    win.current_pass.grid(row=0, column=1, padx=5, pady=5)
    
    ttk.Label(frame, text="New Password:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    win.new_pass = ttk.Entry(frame, width=25, show='*')
    win.new_pass.grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(frame, text="Confirm Password:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    win.confirm_pass = ttk.Entry(frame, width=25, show='*')
    win.confirm_pass.grid(row=2, column=1, padx=5, pady=5)
    
    win.status_label = ttk.Label(win, text="", foreground=WARNING_COLOR, font=BTN_FONT, anchor='center')
    win.status_label.pack(fill='x', pady=(0, 10), padx=20)
    
    btn_frame = ttk.Frame(win)
    btn_frame.pack(pady=(0, 10))
    
    win.save_btn = ttk.Button(btn_frame, text="Save", style='Accent.TButton')
    win.save_btn.pack(side='left', padx=10)
    ttk.Button(btn_frame, text="Cancel", command=win.destroy).pack(side='left', padx=10)
    
    return win

def show_login_window():
    # Clear any existing widgets
    for widget in window.winfo_children():
        widget.pack_forget()
    
    # Create fresh login frame
    login_frame = ttk.Frame(window)
    login_frame.pack(fill='both', expand=True)
    
    # Reset style configurations
    style = ttk.Style()
    style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR_DARK, font=BTN_FONT)
    style.configure('TEntry', font=BTN_FONT, fieldbackground=ENTRY_BG, foreground=TEXT_COLOR_DARK)
    style.configure('TButton', font=BTN_FONT)
    style.configure('TRadiobutton', background=BG_COLOR)
    
    # Rest of your existing show_login_window() code...
    ttk.Label(login_frame, text="Login to System", font=SUBHEADER_FONT, foreground=PRIMARY_COLOR).pack(pady=20)
    
    frame = ttk.Frame(login_frame)
    frame.pack(pady=10, padx=20, fill='x')

    ttk.Label(frame, text="Login As:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    role_var = tk.StringVar(value=STUDENT_ROLE)
    ttk.Radiobutton(frame, text="Student", variable=role_var, value=STUDENT_ROLE).grid(row=0, column=1, padx=5, pady=5, sticky='w')
    ttk.Radiobutton(frame, text="Admin", variable=role_var, value=ADMIN_ROLE).grid(row=0, column=2, padx=5, pady=5, sticky='w')
    
    ttk.Label(frame, text="Username/ID:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    username_entry = ttk.Entry(frame, width=25)
    username_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='we')
    
    ttk.Label(frame, text="Password:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
    password_entry = ttk.Entry(frame, width=25, show='*')
    password_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='we')
    
    status_label = ttk.Label(login_frame, text="", foreground=WARNING_COLOR)
    status_label.pack(pady=5)

    def attempt_login():
        role = role_var.get()
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        
        if not username or not password:
            status_label.config(text="Username and password are required!")
            return
        
        if role == ADMIN_ROLE and check_admin_credentials(username, password):
            login_frame.pack_forget()
            window.current_role = ADMIN_ROLE
            build_menubar()
            show_main_page()
        elif role == STUDENT_ROLE and check_student_credentials(username, password):
            login_frame.pack_forget()
            window.current_role = STUDENT_ROLE
            window.current_student_id = username
            build_menubar()
            show_main_page()
        else:
            status_label.config(text="Invalid credentials!")

    btn_frame = ttk.Frame(login_frame)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Login", command=attempt_login, style='Accent.TButton').pack(side='left', padx=10)
    ttk.Button(btn_frame, text="Cancel", command=window.destroy).pack(side='left', padx=10)

def show_main_page():
    for widget in window.winfo_children():
        widget.pack_forget()
    
    if hasattr(window, 'current_role'):
        if window.current_role == ADMIN_ROLE:
            setup_admin_interface()
        else:
            setup_student_interface(getattr(window, 'current_student_id', None))
    else:
        show_login_window()

def setup_admin_interface():
    # Clear existing widgets
    for widget in window.winfo_children():
        widget.pack_forget()
    
    # Rebuild header and main frames
    header_frame.pack(fill='x', padx=10, pady=10)
    main_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    # Reset all entry fields to editable state
    txt.configure(state='normal')
    txt2.configure(state='normal')
    department_menu.configure(state='normal')
    branch_menu.configure(state='normal')
    program_menu.configure(state='normal')
    clear_btn1.configure(state='normal')
    clear_btn2.configure(state='normal')
    clear_academic_btn.configure(state='normal')
    
    # Clear the fields
    txt.delete(0, 'end')
    txt2.delete(0, 'end')
    department_var.set(DEPARTMENTS[0])
    branch_var.set(BRANCHES[0])
    program_var.set(PROGRAMS[0])
    
    # Rebuild management frames
    for widget in mgmt_frame.winfo_children():
        widget.destroy()
    
    ttk.Button(mgmt_frame, text="Take Attendance", command=TrackImages, style='Success.TButton').pack(side='left', padx=5, fill='x', expand=True)
    ttk.Button(mgmt_frame, text="View All Attendance", command=show_all_attendance, style='Accent.TButton').pack(side='left', padx=5, fill='x', expand=True)
    
    for widget in mgmt_frame2.winfo_children():
        widget.destroy()
    
    ttk.Button(mgmt_frame2, text="Delete Individual Registration", command=delete_individual_registration, style='Warning.TButton').pack(side='left', padx=5, fill='x', expand=True)
    ttk.Button(mgmt_frame2, text="Delete Individual Faces", command=delete_individual_faces, style='Warning.TButton').pack(side='left', padx=5, fill='x', expand=True)
    ttk.Button(mgmt_frame2, text="Delete Individual Attendance", command=delete_individual_attendance, style='Warning.TButton').pack(side='left', padx=5, fill='x', expand=True)
    
    # Reset messages and buttons
    message1.config(text="1) Take Images  >>>  2) Save Profile")
    message.config(text="Total Registrations: 0")
    
    # Rebuild button frame
    for widget in btn_frame.winfo_children():
        widget.destroy()
    
    ttk.Button(btn_frame, text="Capture Images", command=TakeImages, style='Accent.TButton').pack(side='left', padx=5, fill='x', expand=True)
    ttk.Button(btn_frame, text="Save Profile", command=TrainImages, style='Success.TButton').pack(side='left', padx=5, fill='x', expand=True)
    
    # Enable all admin features
    send_btn.configure(state='normal')
    
    title_label.config(text="Face Recognition Attendance System (Admin Mode)")
    build_menubar()
    update_registration_count()  # Refresh the registration count

def setup_student_interface(student_id):
    for widget in mgmt_frame.winfo_children():
        widget.destroy()
    
    ttk.Button(mgmt_frame, text="Take Attendance", command=TrackImages, style='Success.TButton').pack(side='left', padx=5, fill='x', expand=True)
    ttk.Button(mgmt_frame, text="View My Attendance", command=lambda: show_student_attendance(student_id), style='Accent.TButton').pack(side='left', padx=5, fill='x', expand=True)

    for widget in window.winfo_children():
        widget.pack_forget()
    
    header_frame.pack(fill='x', padx=10, pady=10)
    main_frame.pack(fill='both', expand=True, padx=20, pady=10)
    
    student_details = get_student_details(student_id)
    
    txt.delete(0, 'end')
    txt.insert(0, student_id)
    txt.configure(state='readonly')
    
    if student_details:
        txt2.delete(0, 'end')
        txt2.insert(0, student_details['name'])
        txt2.configure(state='readonly')
        department_var.set(student_details['department'])
        branch_var.set(student_details['branch'])
        program_var.set(student_details['program'])
    else:
        txt2.delete(0, 'end')
        txt2.configure(state='disabled')
    
    department_menu.configure(state='disabled')
    branch_menu.configure(state='disabled')
    program_menu.configure(state='disabled')
    clear_btn1.configure(state='disabled')
    clear_btn2.configure(state='disabled')
    clear_academic_btn.configure(state='disabled')
    enable_student_features()
    
    # Update the messages for student mode
    total_students = update_registration_count()
    message1.config(text=f"Total Registered Students: {total_students}")
    
    # Initialize attendance count to 0 (will be updated when viewing attendance)
    message.config(text="Total Attendance Records: 0")
    
    title_label.config(text=f"Face Recognition Attendance System (Student Mode - ID: {student_id})")
    build_menubar()

def show_student_attendance(student_id):
    for item in tv.get_children():
        tv.delete(item)
    
    attendance_dir = "Attendance/"
    if not os.path.exists(attendance_dir):
        mess.showinfo("Info", "No attendance records found!")
        message.config(text="Total Attendance Records: 0")
        return
    
    attendance_files = [os.path.join(attendance_dir, f) for f in os.listdir(attendance_dir) 
                       if f.startswith("Attendance_") and f.endswith(".csv")]
    
    if not attendance_files:
        mess.showinfo("Info", "No attendance records found!")
        message.config(text="Total Attendance Records: 0")
        return
    
    records_found = 0
    for filepath in sorted(attendance_files):
        try:
            with open(filepath, 'r', newline='') as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)  
                    if len(header) < 7:  
                        continue
                except StopIteration:
                    continue
                
                for row in reader:
                    if row and len(row) >= 7 and row[0] == student_id:
                        tv.insert('', 'end', text=row[0], 
                                values=(row[1], row[2], row[3], 
                                       row[4], row[5], row[6]))
                        records_found += 1
        except Exception as e:
            print(f"Error reading {filepath}: {str(e)}")
            continue
    
    if records_found > 0:
        message.config(text=f"Total Attendance Records: {records_found}")
    else:
        message.config(text="Total Attendance Records: 0")

def get_student_details(student_id):
    csv_path = "StudentDetails/StudentDetails.csv"
    if not os.path.isfile(csv_path):
        return None
    
    with open(csv_path, 'r') as csvFile:
        reader = csv.reader(csvFile)
        try:
            header = next(reader)
            if len(header) < 11:  
                csvFile.seek(0)  
        except StopIteration:
            return None  
        
        while True:
            try:
                row1 = next(reader)  
                while not any(field.strip() for field in row1):
                    row1 = next(reader)
                    
                next(reader)
                
                if len(row1) >= 11 and row1[2].strip() == student_id:
                    return {
                        'name': row1[4].strip(),
                        'department': row1[6].strip(),
                        'branch': row1[8].strip(),
                        'program': row1[10].strip()
                    }
            except StopIteration:
                break
    return None

def enable_student_features():
    for widget in btn_frame.winfo_children():
        widget.pack_forget()
    
    for child in (mgmt_frame2.winfo_children() + [send_btn]):
        child.configure(state='disabled')
    
    for child in mgmt_frame.winfo_children():
        child.configure(state='normal')
    
    send_btn.configure(state='normal')
    
    for widget in mgmt_frame2.winfo_children():
        widget.destroy()

def show_all_attendance():
    for item in tv.get_children():
        tv.delete(item)
    
    attendance_dir = "Attendance/"
    if not os.path.exists(attendance_dir):
        mess.showinfo("Info", "No attendance records found!")
        return
    
    attendance_files = [os.path.join(attendance_dir, f) for f in os.listdir(attendance_dir) 
                       if f.startswith("Attendance_") and f.endswith(".csv")]
    
    if not attendance_files:
        mess.showinfo("Info", "No attendance records found!")
        return
    
    records_found = 0
    for filepath in sorted(attendance_files):
        try:
            with open(filepath, 'r', newline='') as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)  
                    if len(header) < 7:  
                        continue
                except StopIteration:
                    continue
                
                for row in reader:
                    if row: 
                        if len(row) >= 7:  
                            tv.insert('', 'end', text=row[0], 
                                    values=(row[1], row[2], row[3], 
                                           row[4], row[5], row[6]))
                            records_found += 1
        except Exception as e:
            print(f"Error reading {filepath}: {str(e)}")
            continue
    
    if records_found > 0:
        message.config(text=f"Found {records_found} attendance records")
    else:
        message.config(text="No attendance records found")

def getImagesAndLabels(path, faceCascade):  
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []
    
    for imagePath in imagePaths:
        try:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img, 'uint8')
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = faceCascade.detectMultiScale(img_numpy)
            
            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
                
        except Exception as e:
            print(f"Error processing image {imagePath}: {str(e)}")
            continue
    
    return faceSamples, ids

def TrainImages():
    check_haarcascadefile()
    assure_path_exists("TrainingImageLabel/")

    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        faces, ids = getImagesAndLabels("TrainingImage", faceCascade)  
        if not faces:
            mess.showerror('Error', 'No valid training data found!')
            return
        recognizer.train(faces, np.array(ids))
        recognizer.save("TrainingImageLabel/Trainner.yml")
        message1.config(text="Profile saved successfully!")
        update_registration_count()
        
        if hasattr(window, 'new_registration_in_progress'):
            window.new_registration_in_progress = False
            window.images_captured_for_current = False
    except Exception as e:
        mess.showerror('Error', f'Training failed!\n{str(e)}')

def TakeImages():
    check_haarcascadefile()
    assure_path_exists("StudentDetails/")
    assure_path_exists("TrainingImage/")
    
    csv_path = "StudentDetails/StudentDetails.csv"
    
    # Get the next available serial number
    serial = 1
    if os.path.isfile(csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            rows = [row for row in reader if any(field.strip() for field in row)]
            
            # Find the maximum serial number in existing records
            serial_numbers = []
            for row in rows[1:]:  # Skip header row
                if row and row[0].isdigit():
                    try:
                        serial_numbers.append(int(row[0]))
                    except ValueError:
                        continue
            
            if serial_numbers:
                serial = max(serial_numbers) + 1
    
    Id = txt.get().strip()
    name = txt2.get().strip()
    department = department_var.get()
    branch = branch_var.get()
    program = program_var.get()
    
    if hasattr(window, 'current_role') and window.current_role == STUDENT_ROLE and Id != window.current_student_id:
        mess.showwarning('Permission Denied', 'Students can only register themselves!')
        return
    
    if not Id or not name:
        mess.showwarning('Input Error', 'Both ID and Name are required!')
        return
    
    if not (name.replace(' ', '').isalpha()):
        mess.showwarning('Input Error', 'Name should contain only alphabets and spaces!')
        return
    
    if window.current_role == ADMIN_ROLE and os.path.isfile(csv_path):
        with open(csv_path, 'r') as csvFile:
            reader = csv.reader(csvFile)
            for row in reader:
                if len(row) > 2 and row[2].strip() == Id and not mess.askyesno('Duplicate ID', f'Student ID {Id} exists! Continue?'):
                    return
                if len(row) > 4 and row[4].strip().lower() == name.lower() and not mess.askyesno('Duplicate Name', f'Name "{name}" exists! Continue?'):
                    return
    
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    sampleNum = 0
    
    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            sampleNum += 1
            cv2.imwrite(f"TrainingImage/{name}.{serial}.{Id}.{sampleNum}.jpg", gray[y:y+h, x:x+w])
            cv2.imshow('Capturing Images', img)
        
        if cv2.waitKey(100) & 0xFF == ord('q') or sampleNum > 50:
            break
    
    cam.release()
    cv2.destroyAllWindows()
    
    try:
        # Check if file exists and is empty to write header
        write_header = not os.path.exists(csv_path) or os.stat(csv_path).st_size == 0
        
        with open(csv_path, 'a', newline='') as csvFile:
            writer = csv.writer(csvFile)
            
            if write_header:
                writer.writerow(['SERIAL NO.', '', 'ID', '', 'NAME', '', 'DEPARTMENT', '', 'BRANCH', '', 'PROGRAM'])
                writer.writerow([''] * 11)  # Empty row after header
            
            # Write student data with proper serial number
            writer.writerow([serial, '', Id, '', name, '', department, '', branch, '', program])
            writer.writerow([''] * 11)  # Empty row after student data
            
        message1.config(text=f"Images captured for ID: {Id}")
        update_registration_count()
        create_student_password(Id)
        
        for btn in btn_frame.winfo_children():
            if "Save Profile" in btn['text']:
                btn.configure(state='normal')
                
    except Exception as e:
        mess.showerror('Error', f'Failed to save student details:\n{str(e)}')

def TrackImages():
    check_haarcascadefile()
    assure_path_exists("Attendance/")
    assure_path_exists("StudentDetails/")
    
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        mess.showerror('Error', 'Could not open camera!')
        return
    
    for item in tv.get_children():
        tv.delete(item)
    
    if not os.path.isfile("TrainingImageLabel/Trainner.yml"):
        mess.showerror('Data Missing', 'Please train the system first!')
        cam.release()
        return
    
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("TrainingImageLabel/Trainner.yml")
    except Exception as e:
        mess.showerror('Error', f'Failed to load trained data:\n{str(e)}')
        cam.release()
        return
    
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    
    df_path = "StudentDetails/StudentDetails.csv"
    if not os.path.isfile(df_path):
        mess.showerror('Missing Data', 'Student details not found!')
        cam.release()
        return

    try:
        students = []
        with open(df_path, 'r') as csvFile:
            reader = csv.reader(csvFile)
            try:
                header = next(reader)  
                if len(header) < 11:  
                    raise StopIteration
            except StopIteration:
                pass  
            while True:
                try:
                    row1 = next(reader)  
                    
                    while not any(field.strip() for field in row1):
                        row1 = next(reader)
                        
                    row2 = next(reader)
                    
                    if len(row1) >= 11:  
                        students.append({
                            'serial': row1[0].strip(),
                            'id': row1[2].strip(),
                            'name': row1[4].strip(),
                            'department': row1[6].strip(),
                            'branch': row1[8].strip(),
                            'program': row1[10].strip()
                        })
                except StopIteration:
                    break
        
        if not students:
            mess.showerror('Error', 'No student records found!')
            cam.release()
            return
            
    except Exception as e:
        mess.showerror('Error', f'Failed to read student details:\n{str(e)}')
        cam.release()
        return
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Department', 'Branch', 'Program', 'Date', 'Time']
    attendance_recorded = False
    
    while True:
        ret, im = cam.read()
        if not ret:
            mess.showerror('Error', 'Failed to capture image from camera!')
            break
        
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.2, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x + w, y + h), (225, 0, 0), 2)
            serial, conf = recognizer.predict(gray[y:y+h, x:x+w])
            
            if conf < 50:
                try:
                    student_info = next((s for s in students if s['serial'] == str(serial)), None)
                    
                    if student_info:
                        aa = student_info['name']
                        Id = student_info['id']
                        department = student_info['department']
                        branch = student_info['branch']
                        program = student_info['program']
                        
                        ts = time.time()
                        date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%I:%M:%S %p')
                        
                        cv2.putText(im, str(aa), (x, y + h), font, 1, (255, 255, 255), 2)
                        
                        if not attendance_recorded:
                            attendance_path = f"Attendance/Attendance_{date}.csv"
                            file_exists = os.path.isfile(attendance_path)
                            
                            with open(attendance_path, 'a+', newline='') as csvFile1:
                                writer = csv.writer(csvFile1)
                                
                                if not file_exists:
                                    writer.writerow(['ID', 'Name', 'Department', 'Branch', 'Program', 'Date', 'Time'])
                                
                                writer.writerow([Id, aa, department, branch, program, date, timeStamp])
                            
                            attendance_recorded = True
                            tv.insert('', 'end', text=Id, values=(aa, department, branch, program, date, timeStamp))
                    else:
                        cv2.putText(im, "Unknown", (x, y + h), font, 1, (255, 255, 255), 2)
                except Exception as e:
                    print(f"Error processing student info: {str(e)}")
                    cv2.putText(im, "Error", (x, y + h), font, 1, (255, 0, 0), 2)
            else:
                cv2.putText(im, "Unknown", (x, y + h), font, 1, (255, 255, 255), 2)
        
        cv2.imshow('Taking Attendance', im)
        if cv2.waitKey(1) == ord('q'):
            break
    
    cam.release()
    cv2.destroyAllWindows()

def update_registration_count():
    csv_path = "StudentDetails/StudentDetails.csv"
    if not os.path.isfile(csv_path):
        message.config(text='Total Registrations: 0')
        return 0
    
    try:
        with open(csv_path, 'r') as f:
            count = 0
            reader = csv.reader(f)
            try:
                header = next(reader)  
                if len(header) < 11:  
                    f.seek(0)  
            except StopIteration:
                pass  
            prev_line_has_data = False
            for row in reader:
                if any(field.strip() for field in row):
                    if not prev_line_has_data:
                        count += 1
                    prev_line_has_data = True
                else:
                    prev_line_has_data = False
            
        message.config(text=f'Total Registrations: {count}')
        return count
    except Exception as e:
        message.config(text='Error counting registrations')
        print(f"Error updating registration count: {str(e)}")
        return 0

def send_email():
    recipient_email = recipient_email_entry.get().strip() + "@" + domain_var.get()
    if not recipient_email:
        mess.showwarning('Input Error', 'Please enter recipient email!')
        return
    
    date = datetime.datetime.now().strftime('%d-%m-%Y')
    filename = f"Attendance/Attendance_{date}.csv"
    if not os.path.isfile(filename):
        mess.showerror('Error', 'No attendance record found for today!')
        return
    
    msg = MIMEMultipart()
    msg['From'] = "badgotiyaaditya18@gmail.com"
    msg['To'] = recipient_email
    msg['Subject'] = f"Attendance Report - {date}"
    msg.attach(MIMEText(f"Please find attached the attendance report for {date}.", 'plain'))
    
    with open(filename, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= Attendance_{date}.csv")
        msg.attach(part)
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("badgotiyaaditya18@gmail.com", "qxmj sjnv oipa mxsl")
        server.sendmail("badgotiyaaditya18@gmail.com", recipient_email, msg.as_string())
        server.quit()
        mess.showinfo('Success', 'Email sent successfully!')
    except Exception as e:
        mess.showerror('Error', f'Failed to send email:\n{str(e)}')

def delete_individual_attendance():
    attendance_dir = "Attendance/"
    if not os.path.exists(attendance_dir):
        mess.showinfo('Error', 'No attendance directory found!')
        return
    
    attendance_files = []
    for f in os.listdir(attendance_dir):
        if f.startswith("Attendance_") and f.endswith(".csv"):
            filepath = os.path.join(attendance_dir, f)
            attendance_files.append(filepath)
    
    if not attendance_files:
        mess.showinfo('Info', 'No attendance records found!')
        return
    
    select_window = tk.Toplevel()
    select_window.title("Delete Individual Attendance")
    select_window.geometry("1000x600")
    select_window.configure(bg=BG_COLOR)
    
    ttk.Label(select_window, text="Select Attendance Records to Delete", 
             font=SUBHEADER_FONT, foreground=PRIMARY_COLOR).pack(pady=10)
    
    date_frame = ttk.Frame(select_window)
    date_frame.pack(fill='x', padx=10, pady=5)
    
    ttk.Label(date_frame, text="Select Date:").pack(side='left', padx=5)
    
    dates = sorted(list(set(
        os.path.basename(f)[11:-4] for f in attendance_files
    )), reverse=True)
    
    date_var = tk.StringVar(value=dates[0] if dates else "")
    date_menu = ttk.Combobox(date_frame, textvariable=date_var, values=dates, state="readonly")
    date_menu.pack(side='left', padx=5, fill='x', expand=True)
    
    def load_attendance_records():
        for item in tree.get_children():
            tree.delete(item)
        
        selected_date = date_var.get()
        if not selected_date:
            return
            
        filepath = f"Attendance/Attendance_{selected_date}.csv"
        if not os.path.exists(filepath):
            mess.showwarning("Warning", f"No attendance file found for {selected_date}")
            return
        
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  
                
                for row in reader:
                    if row:  
                        tree.insert('', 'end', values=row)
        except Exception as e:
            mess.showerror("Error", f"Failed to read attendance file:\n{str(e)}")
    
    ttk.Button(date_frame, text="Load Records", command=load_attendance_records, 
              style='Accent.TButton').pack(side='left', padx=5)
    
    tree_frame = ttk.Frame(select_window)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
    
    tree_scroll_y = ttk.Scrollbar(tree_frame)
    tree_scroll_y.pack(side='right', fill='y')
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
    tree_scroll_x.pack(side='bottom', fill='x')
    
    tree = ttk.Treeview(tree_frame, 
                       columns=('ID', 'Name', 'Department', 'Branch', 'Program', 'Date', 'Time'), 
                       show='headings',
                       yscrollcommand=tree_scroll_y.set,
                       xscrollcommand=tree_scroll_x.set,
                       selectmode='extended')
    
    for col in tree['columns']:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor='center')
    
    tree.column('Name', width=150)
    tree.column('Department', width=120)
    
    tree.pack(fill='both', expand=True)
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)
    
    def delete_selected_records():
        selected_items = tree.selection()
        if not selected_items:
            mess.showwarning('Warning', 'Please select at least one record to delete!')
            return
    
        selected_date = date_var.get()
        if not selected_date:
            return
        
        filepath = f"Attendance/Attendance_{selected_date}.csv"
        if not os.path.exists(filepath):
            mess.showwarning("Warning", f"Attendance file not found for {selected_date}")
            return
    
        selected_ids = set(tree.item(item, 'values')[0] for item in selected_items)
    
        remaining_records = []
        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  
                remaining_records.append(header)
            
                for row in reader:
                    if row and row[0] not in selected_ids:  
                        remaining_records.append(row)
        except Exception as e:
            mess.showerror("Error", f"Failed to read attendance file:\n{str(e)}")
            return
    
        try:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(remaining_records)
        
            for item in selected_items:
                tree.delete(item)
        
            mess.showinfo("Success", f"Deleted {len(selected_items)} attendance records!")
        except Exception as e:
            mess.showerror("Error", f"Failed to save changes:\n{str(e)}")
    
    btn_frame = ttk.Frame(select_window)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="Delete Selected", command=delete_selected_records, 
              style='Warning.TButton').pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Close", command=select_window.destroy).pack(side='left', padx=5)
    
    if dates:
        load_attendance_records()

def delete_individual_registration():
    if not show_file_verification():
        return
    
    csv_path = "StudentDetails/StudentDetails.csv"
    if not os.path.isfile(csv_path):
        mess.showerror("Error", "Student details file not found!")
        return
    
    # Create the delete window
    delete_win = tk.Toplevel()
    delete_win.title("Delete Individual Registration - Admin Mode")
    delete_win.geometry("1000x600")
    
    def load_student_data():
        try:
            students = []
            with open(csv_path, 'r') as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)
                    if len(header) < 11:
                        raise StopIteration
                except StopIteration:
                    pass
                
                while True:
                    try:
                        row1 = next(reader)
                        while not any(field.strip() for field in row1):
                            row1 = next(reader)
                        
                        row2 = next(reader)
                        
                        if len(row1) >= 11:
                            students.append({
                                'serial': row1[0].strip(),
                                'id': row1[2].strip(),
                                'name': row1[4].strip(),
                                'department': row1[6].strip(),
                                'branch': row1[8].strip(),
                                'program': row1[10].strip(),
                                'row1': row1,
                                'row2': row2
                            })
                    except StopIteration:
                        break
            
            return students
        
        except Exception as e:
            mess.showerror("Error", f"Failed to read student data:\n{str(e)}")
            return None
    
    def refresh_treeview():
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        # Reload student data
        students = load_student_data()
        if not students:
            return
        
        # Populate treeview with corrected serial numbers
        for i, student in enumerate(students, 1):
            tree.insert('', 'end', values=(
                i,  # Display corrected serial number
                student['id'],
                student['name'],
                student['department'],
                student['branch'],
                student['program']
            ))
    
    # Treeview setup
    tree_frame = ttk.Frame(delete_win)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    columns = ['Serial', 'ID', 'Name', 'Department', 'Branch', 'Program']
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
    
    col_widths = [60, 100, 200, 150, 120, 120]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor='center')
    
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    
    # Initial data load
    refresh_treeview()
    
    def perform_deletion():
        if not tree.selection():
            mess.showwarning("Warning", "Please select a student record!")
            return
        
        selected_item = tree.selection()[0]
        student_id = tree.item(selected_item, 'values')[1]
        student_name = tree.item(selected_item, 'values')[2]
        
        if not mess.askyesno("Confirm", 
                           f"Delete registration for:\n\nID: {student_id}\nName: {student_name}\n\nThis will remove:\n- Student details\n- Face images\n- Password file\n\nThis cannot be undone!"):
            return
        
        try:
            # Read all student data
            students = load_student_data()
            if not students:
                return
            
            # Find and remove the selected student
            updated_students = [s for s in students if s['id'] != student_id]
            
            if len(updated_students) == len(students):
                mess.showinfo("Info", "Student not found in records!")
                return
            
            # Write the updated data back to file with corrected serial numbers
            with open(csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow(['SERIAL NO.', '', 'ID', '', 'NAME', '', 'DEPARTMENT', '', 'BRANCH', '', 'PROGRAM'])
                writer.writerow([''] * 11)  # Empty line after header
                
                # Write updated student records with corrected serial numbers
                for i, student in enumerate(updated_students, 1):
                    # Update the serial number in the row data
                    student['row1'][0] = str(i)
                    writer.writerow(student['row1'])
                    writer.writerow(student['row2'])
                    writer.writerow([''] * 11)  # Empty line between records
            
            # Delete training images
            training_image_path = "TrainingImage/"
            if os.path.exists(training_image_path):
                for filename in os.listdir(training_image_path):
                    if f".{student_id}." in filename:
                        try:
                            os.remove(os.path.join(training_image_path, filename))
                        except Exception as e:
                            print(f"Error deleting {filename}: {str(e)}")
            
            # Delete password file
            password_file = f"StudentDetails/{student_id}_psd.txt"
            if os.path.exists(password_file):
                try:
                    os.remove(password_file)
                except Exception as e:
                    print(f"Error deleting {password_file}: {str(e)}")
            
            # Update the registration count in main window
            update_registration_count()
            
            # Refresh the treeview
            refresh_treeview()
            
            mess.showinfo("Success", f"Registration deleted for:\n\nID: {student_id}\nName: {student_name}")
            
        except Exception as e:
            mess.showerror("Error", f"Failed to delete registration:\n{str(e)}")
    
    # Button frame
    btn_frame = ttk.Frame(delete_win)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="Delete Selected", command=perform_deletion, 
              style='Warning.TButton').grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Close", command=delete_win.destroy).grid(row=0, column=1, padx=10)
    
    tree_frame.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)

def delete_individual_faces():
    if not show_file_verification():
        return
    
    try:
        csv_path = "StudentDetails/StudentDetails.csv"
        students = []
        
        if not os.path.exists(csv_path):
            mess.showerror("Error", "Student details file not found!")
            return
            
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
                if len(header) < 11:  
                    raise StopIteration
            except StopIteration:
                pass  
            while True:
                try:
                    row1 = next(reader)  
                    while not any(field.strip() for field in row1):
                        row1 = next(reader)
                        
                    row2 = next(reader)
                    
                    if len(row1) >= 11:  
                        students.append({
                            'id': row1[2].strip(),
                            'name': row1[4].strip(),
                            'department': row1[6].strip(),
                            'branch': row1[8].strip(),
                            'program': row1[10].strip()
                        })
                except StopIteration:
                    break
    except Exception as e:
        mess.showerror("Error", f"Failed to read student data:\n{str(e)}")
        return
    
    if not students:
        mess.showinfo("Info", "No student records found in the database!")
        return
    
    image_counts = {}
    image_samples = {}
    training_image_path = "TrainingImage/"
    
    if os.path.exists(training_image_path):
        for filename in os.listdir(training_image_path):
            try:
                parts = filename.split('.')
                if len(parts) >= 3:
                    student_id = parts[2]
                    if student_id not in image_counts:
                        image_counts[student_id] = 0
                        image_samples[student_id] = filename
                    image_counts[student_id] += 1
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                continue
    
    delete_win = tk.Toplevel()
    delete_win.title("Delete Face Images - Admin Mode")
    delete_win.geometry("1200x700")
    
    tree_frame = ttk.Frame(delete_win)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
    columns = ['ID', 'Name', 'Department', 'Branch', 'Program', 'Image Count', 'Sample Image']
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', selectmode='browse')
    
    col_widths = [100, 150, 150, 120, 120, 100, 200]
    for col, width in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor='center')
    
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    
    tree.tag_configure('no_images', foreground='gray')
    
    for student in students:
        student_id = student['id']
        count = image_counts.get(student_id, 0)
        sample = image_samples.get(student_id, "N/A")
        
        tree.insert('', 'end', values=(
            student_id,
            student['name'],
            student['department'],
            student['branch'],
            student['program'],
            count,
            sample
        ), tags=('no_images' if count == 0 else ''))
    
    def perform_deletion():
        if not tree.selection():
            mess.showwarning("Warning", "Please select a student record!")
            return
        
        selected_item = tree.selection()[0]
        student_id = tree.item(selected_item, 'values')[0]
        student_name = tree.item(selected_item, 'values')[1]
        current_count = int(tree.item(selected_item, 'values')[5])
        
        if current_count == 0:
            mess.showinfo("Info", f"No images found for {student_name}")
            return
            
        if not mess.askyesno("Confirm", 
                           f"Delete {current_count} face images for:\n\nID: {student_id}\nName: {student_name}\n\nThis cannot be undone!"):
            return
        
        try:
            deleted_count = 0
            if os.path.exists(training_image_path):
                for filename in os.listdir(training_image_path):
                    if f".{student_id}." in filename:
                        try:
                            os.remove(os.path.join(training_image_path, filename))
                            deleted_count += 1
                        except Exception as e:
                            print(f"Error deleting {filename}: {str(e)}")
            
            tree.item(selected_item, values=(
                student_id,
                student_name,
                tree.item(selected_item, 'values')[2],  
                tree.item(selected_item, 'values')[3],  
                tree.item(selected_item, 'values')[4],  
                0,  
                "N/A"  
            ), tags=('no_images',))
            
            mess.showinfo("Success", f"Deleted {deleted_count} images for:\n\nID: {student_id}\nName: {student_name}")
            
        except Exception as e:
            mess.showerror("Error", f"Failed to delete images:\n{str(e)}")
    
    btn_frame = ttk.Frame(delete_win)
    btn_frame.pack(pady=10)
    
    ttk.Button(btn_frame, text="Delete Selected Images", command=perform_deletion, 
              style='Warning.TButton').grid(row=0, column=0, padx=10)
    ttk.Button(btn_frame, text="Refresh List", command=delete_individual_faces).grid(row=0, column=1, padx=10)
    ttk.Button(btn_frame, text="Close", command=delete_win.destroy).grid(row=0, column=2, padx=10)
    
    tree_frame.columnconfigure(0, weight=1)
    tree_frame.rowconfigure(0, weight=1)

def verify_student_files():
    problems = []
    
    csv_path = "StudentDetails/StudentDetails.csv"
    if not os.path.exists(csv_path):
        problems.append("StudentDetails.csv file not found")
    else:
        try:
            with open(csv_path, 'r') as f:
                if len(next(csv.reader(f))) < 11:
                    problems.append("StudentDetails.csv has incorrect format")
        except Exception as e:
            problems.append(f"Error reading StudentDetails.csv: {str(e)}")
    
    if not os.path.exists("TrainingImage/"):
        problems.append("TrainingImage folder not found")
    
    return problems

def show_file_verification():
    problems = verify_student_files()
    if problems:
        mess.showerror("System Issues", "System verification found issues:\n\n" + "\n".join(problems))
        return False
    return True

def delete_registration_csv():
    if mess.askyesno('Confirm', 'Delete all registration data?'):
        csv_path = "StudentDetails/StudentDetails.csv"
        if os.path.exists(csv_path):
            os.remove(csv_path)
            mess.showinfo('Success', 'Registration data deleted.')
            update_registration_count()
        else:
            mess.showinfo('Error', 'Registration file not found.')

def delete_attendance_csv():
    date = datetime.datetime.now().strftime('%d-%m-%Y')
    csv_path = f"Attendance/Attendance_{date}.csv"
    if os.path.exists(csv_path):
        if mess.askyesno('Confirm', f'Delete attendance data for {date}?'):
            os.remove(csv_path)
            for item in tv.get_children():
                tv.delete(item)
            mess.showinfo('Success', 'Attendance data deleted.')
    else:
        mess.showinfo('Error', f'No attendance record found for {date}.')

def delete_registered_images():
    folder_path = "TrainingImage/"
    if os.path.exists(folder_path):
        if mess.askyesno('Confirm', 'Delete all registered face images?'):
            for filename in os.listdir(folder_path):
                try:
                    os.remove(os.path.join(folder_path, filename))
                except Exception as e:
                    print(f"Error deleting {filename}: {str(e)}")
            mess.showinfo('Success', 'All registered images deleted.')
    else:
        mess.showinfo('Error', 'Training images folder not found.')

def logout():
    # Destroy all popup windows
    for widget in window.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()
    
    # Clear the main window
    for widget in window.winfo_children():
        if hasattr(widget, 'pack_forget'):
            widget.pack_forget()
    
    # Reset all entry fields
    txt.configure(state='normal')
    txt.delete(0, 'end')
    txt2.configure(state='normal')
    txt2.delete(0, 'end')
    department_var.set(DEPARTMENTS[0])
    branch_var.set(BRANCHES[0])
    program_var.set(PROGRAMS[0])
    
    # Clear the attendance treeview
    for item in tv.get_children():
        tv.delete(item)
    
    # Reset messages
    message1.config(text="1) Take Images  >>>  2) Save Profile")
    message.config(text="Total Registrations: 0")
    
    # Reset application state
    window.current_role = None
    window.current_student_id = None
    if hasattr(window, 'new_registration_in_progress'):
        del window.new_registration_in_progress
    if hasattr(window, 'images_captured_for_current'):
        del window.images_captured_for_current
    
    # Rebuild the interface
    build_menubar()
    show_login_window()

# Add this in the build_menubar function
def build_menubar():
    menubar = tk.Menu(window, tearoff=0, bg=SECONDARY_COLOR, fg=TEXT_COLOR, activebackground=ACCENT_COLOR)

    filemenu = tk.Menu(menubar, tearoff=0, bg=SECONDARY_COLOR, fg=TEXT_COLOR, activebackground=ACCENT_COLOR)
    if hasattr(window, 'current_role'):
        filemenu.add_command(label="Change Password", command=change_password)
        if window.current_role == ADMIN_ROLE:
            # Add the reset student password option for admin
            filemenu.add_command(label="Reset Student Password", command=reset_student_password)
        filemenu.add_separator()
    filemenu.add_command(label="Exit", command=window.destroy)
    menubar.add_cascade(label="File", menu=filemenu)

    helpmenu = tk.Menu(menubar, tearoff=0, bg=SECONDARY_COLOR, fg=TEXT_COLOR, activebackground=ACCENT_COLOR)
    helpmenu.add_command(label="Contact Support", command=lambda: mess.showinfo('Contact Us', "For support, please contact us at:\nbadgotiyaaditya18@gmail.com"))
    menubar.add_cascade(label="Help", menu=helpmenu)

    window.config(menu=menubar)

# Add this new function to reset student passwords
def reset_student_password():
    if not hasattr(window, 'current_role') or window.current_role != ADMIN_ROLE:
        mess.showerror("Permission Denied", "Only admin can reset student passwords!")
        return
    
    csv_path = "StudentDetails/StudentDetails.csv"
    if not os.path.isfile(csv_path):
        mess.showerror("Error", "Student details file not found!")
        return
    
    # Create the reset window
    reset_win = tk.Toplevel()
    reset_win.title("Reset Student Password - Admin Mode")
    reset_win.geometry("600x400")
    reset_win.resizable(False, False)
    
    ttk.Label(reset_win, text="Reset Student Password", font=SUBHEADER_FONT, 
             foreground=PRIMARY_COLOR).pack(pady=10)
    
    # Student selection frame
    select_frame = ttk.Frame(reset_win)
    select_frame.pack(fill='x', padx=20, pady=10)
    
    ttk.Label(select_frame, text="Select Student:").pack(side='left', padx=5)
    
    # Get all student IDs and names
    try:
        students = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
                if len(header) < 11:
                    raise StopIteration
            except StopIteration:
                pass
            
            while True:
                try:
                    row1 = next(reader)
                    while not any(field.strip() for field in row1):
                        row1 = next(reader)
                    
                    row2 = next(reader)
                    
                    if len(row1) >= 11:
                        students.append({
                            'id': row1[2].strip(),
                            'name': row1[4].strip()
                        })
                except StopIteration:
                    break
        
        if not students:
            mess.showerror("Error", "No student records found!")
            reset_win.destroy()
            return
            
    except Exception as e:
        mess.showerror("Error", f"Failed to read student data:\n{str(e)}")
        reset_win.destroy()
        return
    
    # Create combobox with student IDs and names
    student_options = [f"{s['id']} - {s['name']}" for s in students]
    student_var = tk.StringVar()
    student_menu = ttk.Combobox(select_frame, textvariable=student_var, 
                               values=student_options, state="readonly")
    student_menu.pack(side='left', padx=5, fill='x', expand=True)
    
    # New password frame
    pass_frame = ttk.Frame(reset_win)
    pass_frame.pack(fill='x', padx=20, pady=10)
    
    ttk.Label(pass_frame, text="New Password:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    new_pass_entry = ttk.Entry(pass_frame, show='*')
    new_pass_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
    
    ttk.Label(pass_frame, text="Confirm Password:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    confirm_pass_entry = ttk.Entry(pass_frame, show='*')
    confirm_pass_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
    
    # Status label
    status_label = ttk.Label(reset_win, text="", foreground=WARNING_COLOR)
    status_label.pack(pady=5)
    
    def perform_reset():
        selected = student_var.get()
        if not selected:
            status_label.config(text="Please select a student!")
            return
        
        student_id = selected.split(" - ")[0]
        new_pass = new_pass_entry.get().strip()
        confirm_pass = confirm_pass_entry.get().strip()
        
        if not new_pass or not confirm_pass:
            status_label.config(text="Both password fields are required!")
            return
        
        if len(new_pass) < MIN_PASSWORD_LENGTH:
            status_label.config(text=f"Password must be at least {MIN_PASSWORD_LENGTH} characters!")
            return
        
        if new_pass != confirm_pass:
            status_label.config(text="Passwords don't match!")
            return
        
        # Update the password file
        password_file = f"StudentDetails/{student_id}_psd.txt"
        try:
            with open(password_file, 'w') as f:
                f.write(hash_password(new_pass))
            
            status_label.config(text=f"Password reset for student {student_id}!", foreground=SUCCESS_COLOR)
            
            # Show the new password to admin
            mess.showinfo("Success", 
                        f"Password reset successful for:\n\nID: {student_id}\nNew Password: {new_pass}\n\nPlease inform the student to change it after login.")
            
            # Clear fields
            new_pass_entry.delete(0, 'end')
            confirm_pass_entry.delete(0, 'end')
            
        except Exception as e:
            status_label.config(text=f"Error resetting password: {str(e)}")
    
    # Button frame
    btn_frame = ttk.Frame(reset_win)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Reset Password", command=perform_reset, 
              style='Accent.TButton').pack(side='left', padx=10)
    ttk.Button(btn_frame, text="Cancel", command=reset_win.destroy).pack(side='left', padx=10)
    
    # Set focus to combobox
    student_menu.focus_set()

def reset_student_password():
    if not hasattr(window, 'current_role') or window.current_role != ADMIN_ROLE:
        mess.showerror("Permission Denied", "Only admin can reset student passwords!")
        return
    
    csv_path = "StudentDetails/StudentDetails.csv"
    if not os.path.isfile(csv_path):
        mess.showerror("Error", "Student details file not found!")
        return
    
    # Create the reset window
    reset_win = tk.Toplevel()
    reset_win.title("Reset Student Password - Admin Mode")
    reset_win.geometry("600x400")
    reset_win.resizable(False, False)
    
    ttk.Label(reset_win, text="Reset Student Password", font=SUBHEADER_FONT, 
             foreground=PRIMARY_COLOR).pack(pady=10)
    
    # Student selection frame
    select_frame = ttk.Frame(reset_win)
    select_frame.pack(fill='x', padx=20, pady=10)
    
    ttk.Label(select_frame, text="Select Student:").pack(side='left', padx=5)
    
    # Get all student IDs and names
    try:
        students = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
                if len(header) < 11:
                    raise StopIteration
            except StopIteration:
                pass
            
            while True:
                try:
                    row1 = next(reader)
                    while not any(field.strip() for field in row1):
                        row1 = next(reader)
                    
                    row2 = next(reader)
                    
                    if len(row1) >= 11:
                        students.append({
                            'id': row1[2].strip(),
                            'name': row1[4].strip()
                        })
                except StopIteration:
                    break
        
        if not students:
            mess.showerror("Error", "No student records found!")
            reset_win.destroy()
            return
            
    except Exception as e:
        mess.showerror("Error", f"Failed to read student data:\n{str(e)}")
        reset_win.destroy()
        return
    
    # Create combobox with student IDs and names
    student_options = [f"{s['id']} - {s['name']}" for s in students]
    student_var = tk.StringVar()
    student_menu = ttk.Combobox(select_frame, textvariable=student_var, 
                               values=student_options, state="readonly")
    student_menu.pack(side='left', padx=5, fill='x', expand=True)
    
    # New password frame
    pass_frame = ttk.Frame(reset_win)
    pass_frame.pack(fill='x', padx=20, pady=10)
    
    ttk.Label(pass_frame, text="New Password:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
    new_pass_entry = ttk.Entry(pass_frame, show='*')
    new_pass_entry.grid(row=0, column=1, padx=5, pady=5, sticky='we')
    
    ttk.Label(pass_frame, text="Confirm Password:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
    confirm_pass_entry = ttk.Entry(pass_frame, show='*')
    confirm_pass_entry.grid(row=1, column=1, padx=5, pady=5, sticky='we')
    
    # Status label
    status_label = ttk.Label(reset_win, text="", foreground=WARNING_COLOR)
    status_label.pack(pady=5)
    
    def perform_reset():
        selected = student_var.get()
        if not selected:
            status_label.config(text="Please select a student!")
            return
        
        student_id = selected.split(" - ")[0]
        new_pass = new_pass_entry.get().strip()
        confirm_pass = confirm_pass_entry.get().strip()
        
        if not new_pass or not confirm_pass:
            status_label.config(text="Both password fields are required!")
            return
        
        if len(new_pass) < MIN_PASSWORD_LENGTH:
            status_label.config(text=f"Password must be at least {MIN_PASSWORD_LENGTH} characters!")
            return
        
        if new_pass != confirm_pass:
            status_label.config(text="Passwords don't match!")
            return
        
        # Update the password file
        password_file = f"StudentDetails/{student_id}_psd.txt"
        try:
            with open(password_file, 'w') as f:
                f.write(hash_password(new_pass))
            
            status_label.config(text=f"Password reset for student {student_id}!", foreground=SUCCESS_COLOR)
            
            # Show the new password to admin
            mess.showinfo("Success", 
                        f"Password reset successful for:\n\nID: {student_id}\nNew Password: {new_pass}\n\nPlease inform the student to change it after login.")
            
            # Clear fields
            new_pass_entry.delete(0, 'end')
            confirm_pass_entry.delete(0, 'end')
            
        except Exception as e:
            status_label.config(text=f"Error resetting password: {str(e)}")
    
    # Button frame
    btn_frame = ttk.Frame(reset_win)
    btn_frame.pack(pady=20)
    
    ttk.Button(btn_frame, text="Reset Password", command=perform_reset, 
              style='Accent.TButton').pack(side='left', padx=10)
    ttk.Button(btn_frame, text="Cancel", command=reset_win.destroy).pack(side='left', padx=10)
    
    # Set focus to combobox
    student_menu.focus_set()

def check_haarcascadefile():
    if not os.path.isfile("haarcascade_frontalface_default.xml"):
        mess.showerror('Missing File', 'Required file missing: haarcascade_frontalface_default.xml\nPlease contact support.')
        window.destroy()

def psw():
    if hasattr(window, 'current_role') and window.current_role == ADMIN_ROLE:
        TrainImages() 
        return
    
    assure_path_exists("TrainingImageLabel/")
    if os.path.isfile("TrainingImageLabel/psd.txt"):
        with open("TrainingImageLabel/psd.txt", "r") as tf:
            key = tf.read()
    else:
        new_pas = tsd.askstring('Set Password', 'Enter a new password:', show='*')
        if new_pas:
            with open("TrainingImageLabel/psd.txt", "w") as tf:
                tf.write(new_pas)
            mess.showinfo('Success', 'New password registered successfully!')
            return
    
    password = tsd.askstring('Authentication', 'Enter Password:', show='*')
    if password == key:
        TrainImages()  
    elif password is not None:
        mess.showerror('Access Denied', 'Incorrect password!')

def on_id_or_name_change(*args):
    if hasattr(window, 'current_role') and window.current_role == ADMIN_ROLE:
        if txt.get().strip() or txt2.get().strip():
            window.new_registration_in_progress = True
            window.images_captured_for_current = False
            for btn in btn_frame.winfo_children():
                if "Save Profile" in btn['text']:
                    btn.configure(state='disabled')

def clear():
    if hasattr(window, 'current_role') and window.current_role == STUDENT_ROLE:
        return
    
    txt.delete(0, 'end')
    txt2.delete(0, 'end')
    message1.config(text="1) Take Images  >>>  2) Save Profile")
    
    if hasattr(window, 'current_role') and window.current_role == ADMIN_ROLE:
        window.new_registration_in_progress = False
        window.images_captured_for_current = False
        for btn in btn_frame.winfo_children():
            if "Save Profile" in btn['text']:
                btn.configure(state='normal')

def clear2():
    if hasattr(window, 'current_role') and window.current_role != STUDENT_ROLE:
        clear()

def clear_academic_fields():
    current_values = {
        'dept': department_var.get(),
        'branch': branch_var.get(),
        'program': program_var.get()
    }
    
    department_var.set(DEPARTMENTS[0])
    branch_var.set(BRANCHES[0])
    program_var.set(PROGRAMS[0])
    
    if current_values['dept'] not in DEPARTMENTS:
        department_menu['values'] = (*department_menu['values'], current_values['dept'])
    if current_values['branch'] not in BRANCHES:
        branch_menu['values'] = (*branch_menu['values'], current_values['branch'])
    if current_values['program'] not in PROGRAMS:
        program_menu['values'] = (*program_menu['values'], current_values['program'])

def tick():
    clock.config(text=time.strftime('%I:%M:%S %p'))
    clock.after(1000, tick)

# Main Window Setup
window = tk.Tk()
window.title("Face Recognition Attendance System")
window.geometry("1280x720")
window.configure(bg=BG_COLOR)

style = ttk.Style()
style.theme_use('clam')
style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR_DARK, font=BTN_FONT)
style.configure('TFrame', background=BG_COLOR)
style.configure('TLabel', background=BG_COLOR, foreground=TEXT_COLOR_DARK)
style.configure('TEntry', fieldbackground=ENTRY_BG, foreground=TEXT_COLOR_DARK, insertcolor=TEXT_COLOR_DARK)
style.configure('TButton', background=SECONDARY_COLOR, foreground=TEXT_COLOR, borderwidth=1)
style.map('TButton', 
          background=[('active', ACCENT_COLOR), ('disabled', DISABLED_COLOR)],
          foreground=[('active', TEXT_COLOR), ('disabled', TEXT_COLOR)])
style.configure('Accent.TButton', background=ACCENT_COLOR, foreground=TEXT_COLOR)
style.configure('Success.TButton', background=SUCCESS_COLOR, foreground=TEXT_COLOR)
style.configure('Warning.TButton', background=WARNING_COLOR, foreground=TEXT_COLOR)
style.configure('Treeview', background=ENTRY_BG, foreground=TEXT_COLOR_DARK, fieldbackground=ENTRY_BG, rowheight=25)
style.configure('Treeview.Heading', background=PRIMARY_COLOR, foreground=TEXT_COLOR, font=BTN_FONT)
style.map('Treeview', background=[('selected', ACCENT_COLOR)], foreground=[('selected', TEXT_COLOR)])
style.configure('TCombobox', fieldbackground=ENTRY_BG, foreground=TEXT_COLOR_DARK)

# Header Frame
header_frame = ttk.Frame(window, style='TFrame')
title_label = ttk.Label(header_frame, text="Face Recognition Attendance System", font=HEADER_FONT, foreground=PRIMARY_COLOR, anchor='center')
title_label.pack(fill='x')

info_frame = ttk.Frame(header_frame, style='TFrame')
ts = time.time()
date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
day, month, year = date.split("-")

month_names = {
    '01': 'January', '02': 'February', '03': 'March', '04': 'April',
    '05': 'May', '06': 'June', '07': 'July', '08': 'August',
    '09': 'September', '10': 'October', '11': 'November', '12': 'December'
}

date_label = ttk.Label(info_frame, text=f"{day}-{month_names[month]}-{year}", font=BTN_FONT, foreground=PRIMARY_COLOR)
date_label.pack(side='left', padx=10)

clock = ttk.Label(info_frame, font=BTN_FONT, foreground=PRIMARY_COLOR)
clock.pack(side='right', padx=10)

logout_btn = ttk.Button(info_frame, text="Logout", command=logout, style='Warning.TButton')
logout_btn.pack(side='right', padx=10)

info_frame.pack(fill='x', pady=5)

# Main Content Frames
main_frame = ttk.Frame(window, style='TFrame')
left_frame = ttk.Frame(main_frame, style='TFrame')
right_frame = ttk.Frame(main_frame, style='TFrame')

left_frame.grid(row=0, column=0, padx=10, pady=5, sticky='nsew')
right_frame.grid(row=0, column=1, padx=10, pady=5, sticky='nsew')
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

# Left Frame Content
left_header = ttk.Label(left_frame, text="Attendance Management", font=SUBHEADER_FONT, foreground=PRIMARY_COLOR, anchor='center')
left_header.pack(fill='x', pady=5)

email_frame = ttk.Frame(left_frame, style='TFrame')
ttk.Label(email_frame, text="Recipient Email:").pack(side='left', padx=5)
recipient_email_entry = ttk.Entry(email_frame, width=20)
recipient_email_entry.pack(side='left', padx=5)
ttk.Label(email_frame, text="@").pack(side='left', padx=2)
domain_var = tk.StringVar(value="gmail.com")
domain_menu = ttk.OptionMenu(email_frame, domain_var, "gmail.com", "yahoo.com", "outlook.com", "hotmail.com")
domain_menu.pack(side='left', padx=5)
send_btn = ttk.Button(email_frame, text="Send Report", command=send_email, style='Accent.TButton')
send_btn.pack(side='right', padx=5)
email_frame.pack(fill='x', pady=5)

mgmt_frame = ttk.Frame(left_frame, style='TFrame')
mgmt_frame.pack(fill='x', pady=5)

tree_frame = ttk.Frame(left_frame, style='TFrame')
tree_scroll_y = ttk.Scrollbar(tree_frame)
tree_scroll_y.pack(side='right', fill='y')
tree_scroll_x = ttk.Scrollbar(tree_frame, orient='horizontal')
tree_scroll_x.pack(side='bottom', fill='x')
tv = ttk.Treeview(tree_frame, columns=('name', 'department', 'branch', 'program', 'date', 'time'), show='headings',
                 yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

tv.heading('#0', text='ID')
tv.heading('name', text='NAME')
tv.heading('department', text='DEPARTMENT')
tv.heading('branch', text='BRANCH')
tv.heading('program', text='PROGRAM')
tv.heading('date', text='DATE')
tv.heading('time', text='TIME')

tv.column('#0', width=80, anchor='center')
tv.column('name', width=150, anchor='center')
tv.column('department', width=120, anchor='center')
tv.column('branch', width=100, anchor='center')
tv.column('program', width=100, anchor='center')
tv.column('date', width=100, anchor='center')
tv.column('time', width=100, anchor='center')

tv.pack(fill='both', expand=True)
tree_scroll_y.config(command=tv.yview)
tree_scroll_x.config(command=tv.xview)
tree_frame.pack(fill='both', expand=True, pady=10)

# Right Frame Content
right_header = ttk.Label(right_frame, text="Student Registration", font=SUBHEADER_FONT, foreground=PRIMARY_COLOR, anchor='center')
right_header.pack(fill='x', pady=5)

form_frame = ttk.Frame(right_frame, style='TFrame')
ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
txt = ttk.Entry(form_frame)
txt.grid(row=0, column=1, padx=5, pady=5, sticky='we')
clear_btn1 = ttk.Button(form_frame, text="Clear", command=clear)
clear_btn1.grid(row=0, column=2, padx=5, pady=5)

ttk.Label(form_frame, text="Student Name:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
txt2 = ttk.Entry(form_frame)
txt2.grid(row=1, column=1, padx=5, pady=5, sticky='we')
clear_btn2 = ttk.Button(form_frame, text="Clear", command=clear2)
clear_btn2.grid(row=1, column=2, padx=5, pady=5)
form_frame.pack(fill='x', pady=10)

academic_frame = ttk.Frame(right_frame, style='TFrame')
department_var = tk.StringVar(value=DEPARTMENTS[0])
department_menu = ttk.Combobox(academic_frame, textvariable=department_var, values=DEPARTMENTS, state='normal')
department_menu.grid(row=0, column=1, padx=5, pady=5, sticky='we')

branch_var = tk.StringVar(value=BRANCHES[0])
branch_menu = ttk.Combobox(academic_frame, textvariable=branch_var, values=BRANCHES, state='normal')
branch_menu.grid(row=1, column=1, padx=5, pady=5, sticky='we')

program_var = tk.StringVar(value=PROGRAMS[0])
program_menu = ttk.Combobox(academic_frame, textvariable=program_var, values=PROGRAMS, state='normal')
program_menu.grid(row=2, column=1, padx=5, pady=5, sticky='we')

clear_academic_btn = ttk.Button(academic_frame, text="Clear Academic Fields", command=clear_academic_fields)
clear_academic_btn.grid(row=0, column=2, rowspan=3, padx=5, pady=5, sticky='ns')
form_frame.columnconfigure(1, weight=1)
academic_frame.columnconfigure(1, weight=1)
academic_frame.pack(fill='x', pady=10)

message1 = ttk.Label(right_frame, text="1) Take Images  >>>  2) Save Profile", anchor='center',
                    background=FRAME_COLOR, foreground=TEXT_COLOR_DARK, relief='solid', padding=5)
message1.pack(fill='x', pady=5, padx=5)

message = ttk.Label(right_frame, text="Total Registrations: 0", anchor='center',
                   background=FRAME_COLOR, foreground=TEXT_COLOR_DARK, relief='solid', padding=5)
message.pack(fill='x', pady=5, padx=5)

btn_frame = ttk.Frame(right_frame, style='TFrame')
ttk.Button(btn_frame, text="Capture Images", command=TakeImages, style='Accent.TButton').pack(side='left', padx=5, fill='x', expand=True)
ttk.Button(btn_frame, text="Save Profile", command=TrainImages, style='Success.TButton').pack(side='left', padx=5, fill='x', expand=True)
btn_frame.pack(fill='x', pady=10)

mgmt_frame2 = ttk.Frame(right_frame, style='TFrame')
mgmt_frame2.pack(fill='x', pady=5)

# Initialize and Start
if __name__ == "__main__":
    create_admin_account()
    window.current_student_id = None
    window.current_role = None
    window.after(100, show_login_window)
    tick()
    window.mainloop()