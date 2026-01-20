import tkinter as tk
from tkinter import font
import math
import ctypes
import time

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
window_height = 130  # Increased to accommodate timer

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
left_click_through_mode = False  # Left click through mode state

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

# Timer variables
timer_label = None
timer_start_time = None
timer_running = False

def create_timer_label():
    """Create a timer label below the text"""
    global timer_label, timer_start_time, timer_running
    
    # Remove existing timer label if it exists
    if timer_label:
        try:
            timer_label.destroy()
        except:
            pass
    
    # Create timer label
    timer_label = tk.Label(
        root,
        text="00:00:00",
        font=('Arial', 12),
        fg='white',
        bg='black',
        justify='center'
    )
    timer_label.pack(pady=(0, 5))
    
    # Start timer if not already running
    if not timer_running:
        timer_start_time = time.time()
        timer_running = True
        update_timer()
    else:
        # Timer already running, just update the display
        update_timer()

def update_timer():
    """Update the timer display"""
    global timer_label, timer_start_time, timer_running
    
    if timer_label and timer_running and timer_start_time:
        elapsed = time.time() - timer_start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        timer_label.config(text=timer_text)
        # Schedule next update
        root.after(1000, update_timer)  # Update every second

# Create timer label
create_timer_label()

# Create gear icon button (always clickable)
gear_button = None
gear_window = None

def create_gear_button():
    """Create a gear icon button that's always clickable"""
    global gear_button, gear_window
    
    # Remove existing gear window if it exists
    if gear_window:
        try:
            gear_window.destroy()
        except:
            pass
        gear_window = None
    
    # Remove existing gear button if it exists
    if gear_button:
        try:
            gear_button.destroy()
        except:
            pass
        gear_button = None
    
    # Create a small button with gear icon on main window
    gear_button = tk.Button(
        root,
        text="⚙",
        font=('Arial', 12),
        fg='white',
        bg='black',
        activebackground='gray',
        activeforeground='white',
        relief='flat',
        borderwidth=0,
        cursor='hand2',
        command=lambda: show_gear_menu()
    )
    
    # Position in top-right corner
    gear_button.place(x=window_width - 30, y=5, width=25, height=25)

def create_gear_window():
    """Create a separate window for gear icon when click-through is enabled"""
    global gear_window
    
    # Remove existing gear window if it exists
    if gear_window:
        try:
            gear_window.destroy()
        except:
            pass
    
    # Create a small separate window for the gear icon
    gear_window = tk.Toplevel(root)
    gear_window.overrideredirect(True)
    gear_window.attributes('-topmost', True)
    gear_window.attributes('-alpha', base_alpha)
    gear_window.configure(bg='black')
    
    # Make it small (30x30)
    gear_window.geometry('30x30')
    
    # Create gear button in the separate window
    gear_btn = tk.Button(
        gear_window,
        text="⚙",
        font=('Arial', 12),
        fg='white',
        bg='black',
        activebackground='gray',
        activeforeground='white',
        relief='flat',
        borderwidth=0,
        cursor='hand2',
        command=lambda: show_gear_menu()
    )
    gear_btn.pack(fill=tk.BOTH, expand=True)
    
    # Position it near the main window's top-right corner
    update_gear_window_position()

def update_gear_window_position():
    """Update gear window position to follow main window"""
    global gear_window
    if gear_window:
        try:
            main_x = root.winfo_x()
            main_y = root.winfo_y()
            # Position at top-right of main window
            gear_x = main_x + window_width - 30
            gear_y = main_y + 5
            gear_window.geometry(f'30x30+{gear_x}+{gear_y}')
        except:
            pass

def periodic_gear_update():
    """Periodically update gear window position"""
    if left_click_through_mode and gear_window:
        update_gear_window_position()
    root.after(100, periodic_gear_update)  # Update every 100ms

def show_gear_menu():
    """Show context menu when gear icon is clicked"""
    global menu_open
    menu_open = True
    update_opacity()
    
    # Get gear button position
    if gear_button:
        x = root.winfo_x() + gear_button.winfo_x() + gear_button.winfo_width()
        y = root.winfo_y() + gear_button.winfo_y() + gear_button.winfo_height()
    else:
        x = root.winfo_x() + window_width - 30
        y = root.winfo_y() + 30
    
    update_menu()
    try:
        context_menu.tk_popup(x, y)
    finally:
        context_menu.grab_release()
        menu_open = False
        update_opacity()

# Create gear button
create_gear_button()

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
        # Update gear window position to follow main window
        update_gear_window_position()
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
    """Update window opacity based on dragging, menu, shift state, and edit mode"""
    global dragging, menu_open, shift_pressed_state, auto_hide_mode, edit_entry, gear_window
    
    # If dragging, menu is open, shift is pressed, or editing text, use full opacity
    if dragging or menu_open or shift_pressed_state or (edit_entry is not None):
        root.attributes('-alpha', 1.0)
        # Update gear window opacity too
        if gear_window:
            try:
                gear_window.attributes('-alpha', 1.0)
            except:
                pass
    elif auto_hide_mode:
        # Auto-hide mode will handle its own opacity in check_cursor_proximity
        # Don't override it here
        pass
    else:
        # Normal state - use base alpha
        root.attributes('-alpha', base_alpha)
        # Update gear window opacity too
        if gear_window:
            try:
                gear_window.attributes('-alpha', base_alpha)
            except:
                pass

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

# Check if Shift key is held for opacity control
def check_shift_key():
    global shift_pressed_state
    try:
        # Check if Shift key is currently pressed
        # VK_LSHIFT = 0xA0, VK_RSHIFT = 0xA1
        shift_pressed = (ctypes.windll.user32.GetAsyncKeyState(0xA0) & 0x8000 != 0) or \
                       (ctypes.windll.user32.GetAsyncKeyState(0xA1) & 0x8000 != 0)
        
        # Update shift_pressed_state for opacity control
        shift_pressed_state = shift_pressed
        
        # Update opacity based on shift state
        update_opacity()
        
        # Continue monitoring
        root.after(50, check_shift_key)  # Check every 50ms
    except Exception as e:
        print(f"DEBUG: Error in check_shift_key: {e}")
        root.after(50, check_shift_key)

# Set left click-through state using Windows API
def set_left_click_through(enabled):
    """Enable or disable left click-through mode using WS_EX_TRANSPARENT"""
    try:
        # Windows API constants
        GWL_EXSTYLE = -20
        WS_EX_TRANSPARENT = 0x00000020
        
        # Get window handle
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        
        if hwnd == 0:
            # Try alternative method
            hwnd = root.winfo_id()
        
        # Get current extended window style
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        
        if enabled:
            # Enable click-through by adding WS_EX_TRANSPARENT
            style |= WS_EX_TRANSPARENT
            print("DEBUG: Enabling left click-through mode")
        else:
            # Disable click-through by removing WS_EX_TRANSPARENT
            style &= ~WS_EX_TRANSPARENT
            print("DEBUG: Disabling left click-through mode")
        
        # Set the new style
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        return True
    except Exception as e:
        print(f"DEBUG: Error setting left click-through: {e}")
        return False

# Check for right mouse button to temporarily disable click-through
def check_right_mouse_button():
    global left_click_through_mode, menu_open
    if not left_click_through_mode:
        return
    
    try:
        # Check if right mouse button is currently pressed
        # VK_RBUTTON = 0x02
        right_button_pressed = (ctypes.windll.user32.GetAsyncKeyState(0x02) & 0x8000 != 0)
        
        # Track when right button was just pressed (for edge detection)
        if not hasattr(check_right_mouse_button, 'last_right_state'):
            check_right_mouse_button.last_right_state = False
            check_right_mouse_button.right_click_time = 0
        
        # Detect right button press (edge detection)
        right_button_just_pressed = right_button_pressed and not check_right_mouse_button.last_right_state
        check_right_mouse_button.last_right_state = right_button_pressed
        
        # Record time when right button was pressed
        if right_button_just_pressed:
            check_right_mouse_button.right_click_time = time.time()
        
        # Get cursor position and window bounds to check if cursor is over window
        cursor_x = root.winfo_pointerx()
        cursor_y = root.winfo_pointery()
        win_x = root.winfo_x()
        win_y = root.winfo_y()
        win_width = root.winfo_width()
        win_height = root.winfo_height()
        
        # Check if cursor is over the window
        cursor_over_window = (win_x <= cursor_x <= win_x + win_width and 
                             win_y <= cursor_y <= win_y + win_height)
        
        # Check if right-click happened recently (within last 3 seconds)
        time_since_right_click = time.time() - check_right_mouse_button.right_click_time if hasattr(check_right_mouse_button, 'right_click_time') else 999
        recent_right_click = time_since_right_click < 3.0
        
        # Keep click-through disabled when:
        # 1. Right button is pressed
        # 2. Menu is open
        # 3. Cursor is over window (to allow right-clicks to work)
        # 4. Right-click happened recently (to ensure menu can be accessed)
        should_disable = right_button_pressed or menu_open or cursor_over_window or recent_right_click
        
        if should_disable:
            if not hasattr(check_right_mouse_button, 'temp_disabled'):
                set_left_click_through(False)
                check_right_mouse_button.temp_disabled = True
                if hasattr(check_right_mouse_button, 'delay_counter'):
                    check_right_mouse_button.delay_counter = 0
        else:
            # Only re-enable click-through when cursor is NOT over window
            # and right button is not pressed and menu is not open and no recent right-click
            if hasattr(check_right_mouse_button, 'temp_disabled') and check_right_mouse_button.temp_disabled:
                if not hasattr(check_right_mouse_button, 'delay_counter'):
                    check_right_mouse_button.delay_counter = 0
                check_right_mouse_button.delay_counter += 1
                # Wait 40 checks (2 seconds at 50ms intervals) before re-enabling
                # This gives enough time for right-clicks to be processed
                if check_right_mouse_button.delay_counter >= 40:
                    set_left_click_through(True)
                    check_right_mouse_button.temp_disabled = False
                    check_right_mouse_button.delay_counter = 0
        
        # Continue monitoring - use faster check when click-through is disabled
        # to be more responsive to right-clicks
        check_interval = 20 if (hasattr(check_right_mouse_button, 'temp_disabled') and 
                               check_right_mouse_button.temp_disabled) else 50
        root.after(check_interval, check_right_mouse_button)
    except Exception as e:
        print(f"DEBUG: Error in check_right_mouse_button: {e}")
        if left_click_through_mode:
            root.after(50, check_right_mouse_button)

# Toggle left click through mode
def toggle_left_click_through():
    global left_click_through_mode
    left_click_through_mode = not left_click_through_mode
    print(f"DEBUG: Left click through mode = {left_click_through_mode}")
    
    if set_left_click_through(left_click_through_mode):
        if left_click_through_mode:
            print("DEBUG: Left click-through enabled - left clicks will pass through")
            print("DEBUG: Right clicks will always work")
            # Create separate gear window (clickable even with click-through)
            create_gear_window()
            # Hide gear button on main window
            if gear_button:
                gear_button.place_forget()
            # Start monitoring right mouse button
            check_right_mouse_button()
        else:
            print("DEBUG: Left click-through disabled - all clicks will be captured")
            # Remove gear window and show gear button on main window
            if gear_window:
                try:
                    gear_window.destroy()
                except:
                    pass
            create_gear_button()
            # Clean up temp_disabled flag
            if hasattr(check_right_mouse_button, 'temp_disabled'):
                delattr(check_right_mouse_button, 'temp_disabled')
            if hasattr(check_right_mouse_button, 'delay_counter'):
                delattr(check_right_mouse_button, 'delay_counter')
    else:
        # Fallback: if Windows API fails, revert the toggle
        left_click_through_mode = not left_click_through_mode
        print("DEBUG: Failed to set left click-through mode")
    
    update_menu()

# Check cursor proximity for auto-hide mode
def check_cursor_proximity():
    global auto_hide_mode, dragging, menu_open, shift_pressed_state, edit_entry
    if not auto_hide_mode:
        return
    
    try:
        # If dragging, menu is open, shift is pressed, or editing text, use full opacity
        if dragging or menu_open or shift_pressed_state or (edit_entry is not None):
            root.attributes('-alpha', 1.0)
            # Update gear window opacity too
            if gear_window:
                try:
                    gear_window.attributes('-alpha', 1.0)
                except:
                    pass
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
        # Update gear window opacity too
        if gear_window:
            try:
                gear_window.attributes('-alpha', alpha)
            except:
                pass
        
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
        
        # Set opacity to 100% when editing
        update_opacity()
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
        
        # Recreate timer label
        create_timer_label()
        
        # Rebind events to label
        label.bind('<Button-1>', start_drag)
        label.bind('<B1-Motion>', on_drag)
        label.bind('<ButtonRelease-1>', stop_drag)
        label.bind('<Button-3>', show_context_menu)
        
        # Restore appropriate opacity after editing
        update_opacity()
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
        
        # Recreate timer label
        create_timer_label()
        
        # Rebind events to label
        label.bind('<Button-1>', start_drag)
        label.bind('<B1-Motion>', on_drag)
        label.bind('<ButtonRelease-1>', stop_drag)
        label.bind('<Button-3>', show_context_menu)
        
        original_text = None
        # Restore appropriate opacity after canceling edit
        update_opacity()
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
    if left_click_through_mode:
        context_menu.add_command(label="Left Click through mode ✓", command=toggle_left_click_through)
    else:
        context_menu.add_command(label="Left Click through mode", command=toggle_left_click_through)
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

# Start periodic gear window position update
periodic_gear_update()

# Run the application
root.mainloop()

