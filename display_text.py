import tkinter as tk
from tkinter import font

# Create the main window
root = tk.Tk()

# Remove window decorations (title bar, borders)
root.overrideredirect(True)

# Make window always on top
root.attributes('-topmost', True)

# Get screen dimensions
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set window size (you can adjust these)
window_width = 400
window_height = 100

# Calculate position to center the window
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Set window position and size
root.geometry(f'{window_width}x{window_height}+{x}+{y}')

# Initialize window position tracking
window_x = x
window_y = y

# Make window background transparent (optional)
root.attributes('-alpha', 0.9)  # 0.0 = fully transparent, 1.0 = fully opaque

# Configure background color
root.configure(bg='black')

# Create a label with the text
label = tk.Label(
    root,
    text="example text",
    font=('Arial', 24, 'bold'),
    fg='white',
    bg='black',
    justify='center'
)

# Center the label in the window
label.pack(expand=True)

# Variable to track if we're in edit mode
edit_entry = None
original_text = None

# Mode state: True = Move mode, False = Lock mode
move_mode = False

# Variables for dragging
start_x = None
start_y = None
dragging = False
# Window position tracking (will be initialized after geometry is set)
window_x = None
window_y = None

# Drag functions
def start_drag(event):
    global start_x, start_y, window_x, window_y, dragging
    print(f"DEBUG: start_drag called - move_mode = {move_mode}")
    print(f"DEBUG: event.x_root = {event.x_root}, event.y_root = {event.y_root}")
    if move_mode:
        start_x = event.x_root
        start_y = event.y_root
        # Get current window position and store it
        window_x = root.winfo_x()
        window_y = root.winfo_y()
        dragging = True
        print(f"DEBUG: Drag started - start_x = {start_x}, start_y = {start_y}")
        print(f"DEBUG: Window position stored - window_x = {window_x}, window_y = {window_y}")
    else:
        print("DEBUG: Move mode is False, drag not started")
        dragging = False

def on_drag(event):
    global start_x, start_y, window_x, window_y
    print(f"DEBUG: on_drag called - move_mode = {move_mode}, dragging = {dragging}")
    print(f"DEBUG: event.x_root = {event.x_root}, event.y_root = {event.y_root}")
    print(f"DEBUG: start_x = {start_x}, start_y = {start_y}")
    print(f"DEBUG: window_x = {window_x}, window_y = {window_y}")
    if move_mode and dragging and start_x is not None and start_y is not None and window_x is not None and window_y is not None:
        # Calculate new position based on stored window position
        x = window_x + (event.x_root - start_x)
        y = window_y + (event.y_root - start_y)
        print(f"DEBUG: New position calculated - x = {x}, y = {y}")
        root.geometry(f'+{x}+{y}')
        # Update stored window position
        window_x = x
        window_y = y
        # Update start position for next drag event
        start_x = event.x_root
        start_y = event.y_root
        print(f"DEBUG: Window moved, updated window_x = {window_x}, window_y = {window_y}")
    else:
        if not move_mode:
            print("DEBUG: Move mode is False, drag ignored")
        elif not dragging:
            print("DEBUG: Not dragging (start_drag not called), drag ignored")
        else:
            print("DEBUG: start_x, start_y, window_x, or window_y is None, drag ignored")

# Close window function
def close_window(event=None):
    root.destroy()

# Set move mode
def set_move_mode():
    global move_mode
    print("DEBUG: set_move_mode called")
    move_mode = True
    print(f"DEBUG: move_mode set to {move_mode}")
    update_menu()

# Set lock mode
def set_lock_mode():
    global move_mode
    print("DEBUG: set_lock_mode called")
    move_mode = False
    print(f"DEBUG: move_mode set to {move_mode}")
    update_menu()

# Enable text editing
def edit_text():
    global label, edit_entry, original_text
    print("DEBUG: edit_text called")
    if edit_entry is None:  # Only create if not already editing
        # Get current text and store it as original
        original_text = label.cget("text")
        # Destroy the label
        label.destroy()
        # Create entry widget with same styling
        edit_entry = tk.Entry(
            root,
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='black',
            insertbackground='white',
            justify='center',
            relief='flat',
            borderwidth=0,
            highlightthickness=0
        )
        edit_entry.insert(0, original_text)
        edit_entry.pack(expand=True)
        edit_entry.focus_set()
        edit_entry.select_range(0, tk.END)
        
        # Bind events to save on Enter or focus out
        edit_entry.bind('<Return>', save_text)
        edit_entry.bind('<FocusOut>', save_text)
        edit_entry.bind('<Escape>', cancel_edit)
        
        # Rebind drag events to entry
        edit_entry.bind('<Button-1>', start_drag)
        edit_entry.bind('<B1-Motion>', on_drag)
        edit_entry.bind('<ButtonRelease-1>', stop_drag)
        edit_entry.bind('<Button-3>', show_context_menu)
        
        update_menu()

# Save edited text
def save_text(event=None):
    global label, edit_entry, original_text
    print("DEBUG: save_text called")
    if edit_entry is not None:
        new_text = edit_entry.get()
        # Destroy the entry
        edit_entry.destroy()
        edit_entry = None
        original_text = None
        # Recreate the label with new text
        label = tk.Label(
            root,
            text=new_text,
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='black',
            justify='center'
        )
        label.pack(expand=True)
        
        # Rebind events to label
        label.bind('<Button-1>', start_drag)
        label.bind('<B1-Motion>', on_drag)
        label.bind('<ButtonRelease-1>', stop_drag)
        label.bind('<Button-3>', show_context_menu)
        
        update_menu()

# Cancel editing
def cancel_edit(event=None):
    global label, edit_entry, original_text
    print("DEBUG: cancel_edit called")
    if edit_entry is not None and original_text is not None:
        # Destroy the entry
        edit_entry.destroy()
        edit_entry = None
        # Recreate the label with original text
        label = tk.Label(
            root,
            text=original_text,
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='black',
            justify='center'
        )
        label.pack(expand=True)
        
        # Rebind events to label
        label.bind('<Button-1>', start_drag)
        label.bind('<B1-Motion>', on_drag)
        label.bind('<ButtonRelease-1>', stop_drag)
        label.bind('<Button-3>', show_context_menu)
        
        original_text = None
        update_menu()

# Update context menu to show current mode
def update_menu():
    context_menu.delete(0, tk.END)
    if move_mode:
        context_menu.add_command(label="Move mode ✓", command=set_move_mode)
        context_menu.add_command(label="Lock mode", command=set_lock_mode)
    else:
        context_menu.add_command(label="Move mode", command=set_move_mode)
        context_menu.add_command(label="Lock mode ✓", command=set_lock_mode)
    context_menu.add_separator()
    if edit_entry is None:
        context_menu.add_command(label="Edit text", command=edit_text)
    else:
        context_menu.add_command(label="Finish editing", command=save_text)
    context_menu.add_separator()
    context_menu.add_command(label="Close", command=close_window)

# Create right-click context menu
context_menu = tk.Menu(root, tearoff=0)
update_menu()

# Function to show context menu on right-click
def show_context_menu(event):
    update_menu()  # Update menu to show current mode
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()

# Stop dragging when mouse button is released
def stop_drag(event):
    global dragging, window_x, window_y
    print("DEBUG: stop_drag called")
    dragging = False
    # Update window position from actual window position
    window_x = root.winfo_x()
    window_y = root.winfo_y()
    print(f"DEBUG: Updated window position after drag - window_x = {window_x}, window_y = {window_y}")

# Bind mouse events for dragging (only works in move mode)
root.bind('<Button-1>', start_drag)
root.bind('<B1-Motion>', on_drag)
root.bind('<ButtonRelease-1>', stop_drag)
label.bind('<Button-1>', start_drag)
label.bind('<B1-Motion>', on_drag)
label.bind('<ButtonRelease-1>', stop_drag)

# Bind right-click to show context menu
root.bind('<Button-3>', show_context_menu)
label.bind('<Button-3>', show_context_menu)

# Handle Escape key - cancel editing if in edit mode, otherwise close window
def handle_escape(event=None):
    global edit_entry
    if edit_entry is not None:
        cancel_edit()
    else:
        close_window()

root.bind('<Escape>', handle_escape)

# Run the application
root.mainloop()

