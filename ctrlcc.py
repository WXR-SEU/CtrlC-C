import os
import sys
import keyboard
from pystray import MenuItem as item
import pystray
from PIL import Image
from ctypes import windll
import winreg as reg
import win32event
import win32api
from winerror import ERROR_ALREADY_EXISTS
import re
import time
import win32clipboard as wcb
import win32con
import pywintypes

# Precompiled regex patterns for performance
RE_NEWLINES = re.compile(r"(\r\n|\r|\n)+")
RE_SPACES = re.compile(r"[ \t\u00A0\u2000-\u200A\u202F\u205F\u3000]+")


DOUBLE_PRESS_THRESHOLD = 1.0  # seconds
POST_COPY_DELAY = 0.1  # seconds, allow the second Ctrl+C to update clipboard




def show_message_box(title, message):
    """Show a message box with the given title and message."""
    return windll.user32.MessageBoxW(0, message, title, 0)


def toggle_strip_blankspace(icon, item):
    """Toggle whether to remove blank space from copied text."""
    global is_strip_blankspace
    is_strip_blankspace = not is_strip_blankspace
    return is_strip_blankspace


def strip_newlines(text):
    """Remove all types of newline characters from a string."""
    try:
        # Collapse any sequence of CR/LF into a single space
        return RE_NEWLINES.sub(" ", text)
    except Exception as e:
        return ""


def strip_blankspace(text):
    """Remove all types of blank space characters from a string."""
    try:
        # Remove common space characters: normal space, no-break space, tabs and a range of unicode spaces
        return RE_SPACES.sub("", text)
    except Exception as e:
        return ""


def get_clipboard_text():
    """Windows: robustly read Unicode text from clipboard with retries."""
    for _ in range(5):
        try:
            wcb.OpenClipboard()
            try:
                if wcb.IsClipboardFormatAvailable(wcb.CF_UNICODETEXT):
                    data = wcb.GetClipboardData(wcb.CF_UNICODETEXT)
                    return data if isinstance(data, str) else str(data)
                return ""
            finally:
                wcb.CloseClipboard()
        except pywintypes.error:
            time.sleep(0.03)
        except Exception:
            time.sleep(0.03)
    return ""


def set_clipboard_text(text):
    """Windows: robustly write Unicode text to clipboard with retries."""
    if text is None:
        text = ""
    for _ in range(5):
        try:
            wcb.OpenClipboard()
            try:
                wcb.EmptyClipboard()
                wcb.SetClipboardData(wcb.CF_UNICODETEXT, text)
                return True
            finally:
                wcb.CloseClipboard()
        except pywintypes.error:
            time.sleep(0.03)
        except Exception:
            time.sleep(0.03)
    return False


def on_c_press(event):
    """Detect Ctrl held and double press of 'C' within threshold, no timers."""
    global last_c_time
    if keyboard.is_pressed('ctrl'):
        now = time.monotonic()
        if last_c_time and (now - last_c_time) <= DOUBLE_PRESS_THRESHOLD:
            last_c_time = 0.0
            perform_clipboard_action()
        else:
            last_c_time = now
    else:
        last_c_time = 0.0


# Conflict check removed for Windows-only lightweight build


def perform_clipboard_action():
    """Perform the action of copying the clipboard text and removing newlines."""
    time.sleep(POST_COPY_DELAY)
    current_data = get_clipboard_text()
    if not current_data:
        return
    processed = strip_newlines(current_data)
    if is_strip_blankspace:
        processed = strip_blankspace(processed)
    if processed != current_data:
        set_clipboard_text(processed)


# Timer-based state removed


def create_icon(image_name):
    """The application is frozen"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    # The application is not frozen
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Correct the path to the icon file
    icon_path = os.path.join(base_path, image_name)
    try:
        return Image.open(icon_path)
    except Exception:
        # Fallback: create a simple solid-color icon to avoid crashing if the ICO is missing
        return Image.new("RGB", (64, 64), (40, 110, 140))


def setup_tray_icon():
    """Load your own image as icon and setup tray icon with menu"""
    icon_image = create_icon("ctrlcc.ico")

    # The menu that will appear when the user right-clicks the icon
    menu = (item('Toggle Strip Blank Space', toggle_strip_blankspace,
                 checked=lambda item: is_strip_blankspace),
            item('Exit', exit_program),)
    icon = pystray.Icon("test_icon", icon_image, "CtrlC+C", menu)
    icon.run()


def exit_program(icon, item):
    """Exit the program and stop the system tray icon"""
    icon.stop()  # This will stop the system tray icon and the associated message loop.
    keyboard.unhook_all()
    # print("Exiting program...")


def cleanup_startup_entry():
    """Best-effort removal of any existing startup registry entry."""
    try:
        key = reg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        key_handle = reg.OpenKey(key, key_value, 0, reg.KEY_ALL_ACCESS)
        try:
            reg.DeleteValue(key_handle, "CtrlC+C")
        finally:
            reg.CloseKey(key_handle)
    except Exception:
        pass


if __name__ == "__main__":
    last_c_time = 0.0
    is_strip_blankspace = False

    # Ensure any legacy startup entry is removed
    cleanup_startup_entry()

    mutex_name = "CtrlC_C_Application_Mutex"

    mutex = win32event.CreateMutex(None, False, mutex_name)
    last_error = win32api.GetLastError()

    if last_error == ERROR_ALREADY_EXISTS:
        show_message_box("应用程序已运行", "CtrlC+C 应用程序已经在运行了。")
        sys.exit(0)

    # Instruction message box removed by user request

    # Initialization and event hooks
    keyboard.on_release_key('c', on_c_press)
    setup_tray_icon()  # Start the system tray icon
