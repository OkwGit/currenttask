import tkinter as tk
from tkinter import font
import math
import ctypes

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

# Base transparency settings
base_alpha = 0.9  # Normal transparency
auto_hide_mode = False  # Auto hide mode state
click_through_mode = False  # Click through mode state

# Track states that require full opacity
menu_open = False
shift_pressed_state = False

# Make window background transparent (optional)
root.attributes('-alpha', base_alpha)  # 0.0 = fully transparent, 1.0 = fully opaque

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
        # Set opacity to 100% when dragging
        update_opacity()
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

# Update opacity based on current state
def update_opacity():
    """Update window opacity based on dragging, menu, and shift state"""
    global dragging, menu_open, shift_pressed_state, auto_hide_mode
    
    # If dragging, menu is open, or shift is pressed, use full opacity
    if dragging or menu_open or shift_pressed_state:
        root.attributes('-alpha', 1.0)
    elif auto_hide_mode:
        # Auto-hide mode will handle its own opacity in check_cursor_proximity
        # Don't override it here
        pass
    else:
        # Normal state - use base alpha
        root.attributes('-alpha', base_alpha)

# Toggle auto hide mode
def toggle_auto_hide():
    global auto_hide_mode
    auto_hide_mode = not auto_hide_mode
    print(f"DEBUG: Auto hide mode = {auto_hide_mode}")
    if auto_hide_mode:
        check_cursor_proximity()
    else:
        # Restore appropriate alpha based on current state
        update_opacity()
    update_menu()

# Set click-through state using Windows API
def set_click_through(enabled):
    """Enable or disable click-through mode using WS_EX_TRANSPARENT"""
    try:
        # Windows API constants
        GWL_EXSTYLE = -20
        WS_EX_TRANSPARENT = 0x00000020
        
        # Get window handle - tkinter uses a different method
        # For tkinter, we need to get the root window's handle
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        
        if hwnd == 0:
            # Try alternative method
            hwnd = root.winfo_id()
        
        # Get current extended window style
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        
        if enabled:
            # Enable click-through by adding WS_EX_TRANSPARENT
            style |= WS_EX_TRANSPARENT
            print("DEBUG: Enabling click-through mode")
        else:
            # Disable click-through by removing WS_EX_TRANSPARENT
            style &= ~WS_EX_TRANSPARENT
            print("DEBUG: Disabling click-through mode")
        
        # Set the new style
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        return True
    except Exception as e:
        print(f"DEBUG: Error setting click-through: {e}")
        return False

# Check if Shift key is held and temporarily disable click-through if needed
def check_shift_key():
    global click_through_mode, shift_pressed_state
    try:
        # Check if Shift key is currently pressed
        # VK_LSHIFT = 0xA0, VK_RSHIFT = 0xA1
        shift_pressed = (ctypes.windll.user32.GetAsyncKeyState(0xA0) & 0x8000 != 0) or \
                       (ctypes.windll.user32.GetAsyncKeyState(0xA1) & 0x8000 != 0)
        
        # Update shift_pressed_state (always track, not just in click-through mode)
        shift_pressed_state = shift_pressed
        
        # Only handle click-through logic if click-through mode is enabled
        if click_through_mode:
            # Temporarily disable click-through when Shift is held
            if shift_pressed:
                if not hasattr(check_shift_key, 'temp_disabled'):
                    set_click_through(False)
                    check_shift_key.temp_disabled = True
            else:
                if hasattr(check_shift_key, 'temp_disabled') and check_shift_key.temp_disabled:
                    set_click_through(True)
                    check_shift_key.temp_disabled = False
        
        # Update opacity based on shift state
        update_opacity()
        
        # Always continue monitoring (even when click-through is disabled)
        root.after(50, check_shift_key)  # Check every 50ms
    except Exception as e:
        print(f"DEBUG: Error in check_shift_key: {e}")
        root.after(50, check_shift_key)

# Toggle click through mode
def toggle_click_through():
    global click_through_mode
    click_through_mode = not click_through_mode
    print(f"DEBUG: Click through mode = {click_through_mode}")
    
    if set_click_through(click_through_mode):
        if click_through_mode:
            print("DEBUG: Click-through enabled - clicks will pass through")
            print("DEBUG: Use Shift+Right-click to access menu")
        else:
            print("DEBUG: Click-through disabled - clicks will be captured")
            # Clean up temp_disabled flag
            if hasattr(check_shift_key, 'temp_disabled'):
                delattr(check_shift_key, 'temp_disabled')
    else:
        # Fallback: if Windows API fails, revert the toggle
        click_through_mode = not click_through_mode
        print("DEBUG: Failed to set click-through mode")
    
    update_menu()

# Check cursor proximity for auto-hide mode
def check_cursor_proximity():
    global auto_hide_mode, dragging, menu_open, shift_pressed_state
    if not auto_hide_mode:
        return
    
    try:
        # If dragging, menu is open, or shift is pressed, use full opacity
        if dragging or menu_open or shift_pressed_state:
            root.attributes('-alpha', 1.0)
            # Schedule next check
            root.after(50, check_cursor_proximity)
            return
        
        # Get cursor position (screen coordinates)
        cursor_x = root.winfo_pointerx()
        cursor_y = root.winfo_pointery()
        
        # Get actual window position and size (including the black box)
        win_x = root.winfo_x()
        win_y = root.winfo_y()
        win_width = root.winfo_width()
        win_height = root.winfo_height()
        
        # Calculate the closest point on the window to the cursor
        # Clamp cursor position to window bounds
        closest_x = max(win_x, min(cursor_x, win_x + win_width))
        closest_y = max(win_y, min(cursor_y, win_y + win_height))
        
        # Calculate distance from cursor to the closest point on the window
        distance = math.sqrt((cursor_x - closest_x)**2 + (cursor_y - closest_y)**2)
        
        # Define proximity threshold (pixels) - adjust as needed
        # This determines how close the cursor needs to be to trigger fade
        proximity_threshold = 150
        
        # Calculate alpha based on distance
        # When cursor is close (distance = 0): 2% transparency (0.02 alpha)
        # When cursor is far (distance >= threshold): base_alpha (0.9)
        if distance >= proximity_threshold:
            # Far away - restore to base alpha
            alpha = base_alpha
        else:
            # Close - gradually fade to 2%
            # Map distance from 0 to threshold to alpha from 0.02 to base_alpha
            ratio = distance / proximity_threshold
            alpha = 0.02 + (base_alpha - 0.02) * ratio
        
        # Ensure alpha is within bounds
        alpha = max(0.02, min(base_alpha, alpha))
        
        root.attributes('-alpha', alpha)
        
        # Schedule next check (check every 50ms for smooth transitions)
        root.after(50, check_cursor_proximity)
    except Exception as e:
        # Window might be destroyed or error occurred
        print(f"DEBUG: Error in check_cursor_proximity: {e}")
        if auto_hide_mode:
            root.after(50, check_cursor_proximity)  # Keep checking

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
    if auto_hide_mode:
        context_menu.add_command(label="Auto hide mode ✓", command=toggle_auto_hide)
    else:
        context_menu.add_command(label="Auto hide mode", command=toggle_auto_hide)
    if click_through_mode:
        context_menu.add_command(label="Click through mode ✓", command=toggle_click_through)
    else:
        context_menu.add_command(label="Click through mode", command=toggle_click_through)
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
    global menu_open
    # If click-through mode is enabled, only show menu when Shift is held
    if click_through_mode:
        # Check if Shift key is pressed (state bit 0x0001 is Shift)
        shift_pressed = (event.state & 0x0001) != 0
        if not shift_pressed:
            print("DEBUG: Click-through mode active - Shift+Right-click required")
            return
        print("DEBUG: Shift+Right-click detected in click-through mode")
    
    menu_open = True
    # Set opacity to 100% when menu opens
    update_opacity()
    
    update_menu()  # Update menu to show current mode
    try:
        context_menu.tk_popup(event.x_root, event.y_root)
    finally:
        context_menu.grab_release()
        menu_open = False
        # Restore appropriate opacity after menu closes
        update_opacity()

# Stop dragging when mouse button is released
def stop_drag(event):
    global dragging, window_x, window_y
    print("DEBUG: stop_drag called")
    dragging = False
    # Update window position from actual window position
    window_x = root.winfo_x()
    window_y = root.winfo_y()
    # Restore appropriate opacity after dragging stops
    update_opacity()
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

# Start monitoring Shift key for opacity control
check_shift_key()

# Run the application
root.mainloop()

