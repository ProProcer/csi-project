import tkinter as tk
from datetime import datetime
import csv
import os
import time

class TimeTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Motion Time Tracker")
        self.root.geometry("600x450")
        
        # Set window background
        self.root.configure(bg="#f0f0f0")
        
        # Initialize variables
        self.is_recording = False
        self.start_time = None
        self.current_motion = None
        self.csv_file = "motion_times.csv"
        self.running = True
        
        # Create CSV file if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Start Time", "Stop Time", "Motion"])
        
        # Create main frame
        main_frame = tk.Frame(root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title label
        title_label = tk.Label(main_frame, text="Motion Time Tracker", 
                             font=("Arial", 16, "bold"), bg="#f0f0f0")
        title_label.pack(pady=10)
        
        # Live time display
        self.live_time_var = tk.StringVar()
        self.live_time_var.set("Current Time: --:--:--:------")
        self.live_time_display = tk.Label(main_frame, textvariable=self.live_time_var, 
                                        bg="#f0f0f0", font=("Courier", 12))
        self.live_time_display.pack(pady=5)
        
        # Status display
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to start recording")
        self.status_display = tk.Label(main_frame, textvariable=self.status_var, 
                                      bg="#f0f0f0", font=("Arial", 10))
        self.status_display.pack(pady=10)
        
        # Current motion display
        self.motion_var = tk.StringVar()
        self.motion_var.set("No motion recording")
        self.motion_display = tk.Label(main_frame, textvariable=self.motion_var, 
                                     bg="#f0f0f0", font=("Arial", 12, "bold"), fg="#FF5252")
        self.motion_display.pack(pady=5)
        
        # Instructions frame
        instr_frame = tk.Frame(main_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=1)
        instr_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Instructions header
        instr_label = tk.Label(instr_frame, text="Keyboard Controls:", 
                              bg="#f0f0f0", font=("Arial", 12, "bold"))
        instr_label.pack(anchor="w", padx=10, pady=5)
        
        # Instructions content
        instructions = [
            "Press 'Q' to start/stop recording 'squat'",
            "Press 'W' to start/stop recording 'bicep_curl'",
            "Press 'E' to start/stop recording 'jumping_jack'"
        ]
        
        for instr in instructions:
            instr_item = tk.Label(instr_frame, text=instr, 
                                 bg="#f0f0f0", font=("Arial", 10), anchor="w")
            instr_item.pack(fill=tk.X, padx=15, pady=2)
        
        # Elapsed time (only shown when recording)
        self.elapsed_var = tk.StringVar()
        self.elapsed_var.set("")
        self.elapsed_display = tk.Label(main_frame, textvariable=self.elapsed_var, 
                                       bg="#f0f0f0", font=("Courier", 12))
        self.elapsed_display.pack(pady=5)
        
        # Recent records label
        recent_label = tk.Label(main_frame, text="Recent Records:", 
                               bg="#f0f0f0", font=("Arial", 10, "bold"))
        recent_label.pack(anchor="w")
        
        # Recent records display
        self.recent_var = tk.StringVar()
        self.recent_var.set("No records yet")
        self.recent_display = tk.Label(main_frame, textvariable=self.recent_var, 
                                      bg="#f0f0f0", justify=tk.LEFT)
        self.recent_display.pack(anchor="w")
        
        # Bind keyboard events
        self.root.bind('q', lambda event: self.toggle_motion("squat"))
        self.root.bind('Q', lambda event: self.toggle_motion("squat"))
        self.root.bind('w', lambda event: self.toggle_motion("bicep_curl"))
        self.root.bind('W', lambda event: self.toggle_motion("bicep_curl"))
        self.root.bind('e', lambda event: self.toggle_motion("jumping_jack"))
        self.root.bind('E', lambda event: self.toggle_motion("jumping_jack"))
        
        # Load recent records
        self.load_recent_records()
        
        # Start the live clock update
        self.update_live_time()
    
    def update_live_time(self):
        if self.running:
            # Update current time with microseconds
            current_time = datetime.now()
            time_str = current_time.strftime("%H:%M:%S:%f")
            # Only display first 6 digits of microseconds
            time_str = time_str[:-3]
            self.live_time_var.set(f"Current Time: {time_str}")
            
            # Update elapsed time if recording
            if self.is_recording:
                elapsed = current_time - self.start_time
                total_seconds = elapsed.total_seconds()
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                microseconds = elapsed.microseconds
                elapsed_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}.{microseconds//1000:03d}"
                self.elapsed_var.set(f"Elapsed: {elapsed_str}")
            
            # Schedule the next update (every 50ms for reasonable UI performance)
            self.root.after(50, self.update_live_time)
    
    def toggle_motion(self, motion_name):
        # If currently recording a different motion, ignore the key press
        if self.is_recording and motion_name != self.current_motion:
            return
            
        if not self.is_recording:
            # Start recording
            self.start_time = datetime.now()
            self.current_motion = motion_name
            self.is_recording = True
            start_time_str = self.start_time.strftime("%H:%M:%S.%f")[:-3]
            self.status_var.set(f"Recording started at {start_time_str}")
            self.motion_var.set(f"Recording: {motion_name}")
        else:
            # Stop recording
            stop_time = datetime.now()
            
            # Save to CSV with microsecond precision
            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    self.start_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                    stop_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                    self.current_motion
                ])
            
            # Reset state
            self.is_recording = False
            
            # Update status
            duration = stop_time - self.start_time
            total_seconds = duration.total_seconds()
            minutes, seconds = divmod(total_seconds, 60)
            microseconds = duration.microseconds
            self.status_var.set(f"Recorded '{self.current_motion}' ({int(minutes)}m {int(seconds)}s.{microseconds//1000:03d}ms)")
            self.motion_var.set("No motion recording")
            self.elapsed_var.set("")
            self.current_motion = None
            
            # Update recent records display
            self.load_recent_records()
    
    def load_recent_records(self):
        try:
            with open(self.csv_file, 'r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                records = list(reader)
            
            if records:
                # Get the most recent 3 records
                recent = records[-3:]
                recent_text = "\n".join([
                    f"{row[2]}: {row[0].split(' ')[1]} to {row[1].split(' ')[1]}" 
                    for row in reversed(recent)
                ])
                self.recent_var.set(recent_text)
            else:
                self.recent_var.set("No records yet")
        except FileNotFoundError:
            self.recent_var.set("No records yet")

    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()