import sys
from PyQt6.QtWidgets import QApplication
from database.connection import create_connection
from services.auth_service import setup_admin_password


def load_saved_settings():
    """Read branding settings from database and apply them."""
    try:
        conn = create_connection()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute(
            "SELECT [key], [value] FROM settings"
        )
        settings = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()

        # Apply primary colour to the styles module
        primary_color = settings.get("primary_color", "").strip()
        if primary_color and primary_color.startswith("#") and len(primary_color) == 7:
            from assets import styles
            styles.COLORS["accent"]       = primary_color
            styles.COLORS["accent_hover"] = _darken(primary_color)
            styles.COLORS["accent_light"] = _lighten(primary_color)
            styles.COLORS["accent_text"]  = _darken(primary_color)
            styles.COLORS["success"]      = primary_color

        return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}


def _darken(hex_color, factor=0.8):
    """Darken a hex colour by a factor."""
    try:
        hex_color = hex_color.lstrip("#")
        r = int(int(hex_color[0:2], 16) * factor)
        g = int(int(hex_color[2:4], 16) * factor)
        b = int(int(hex_color[4:6], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return hex_color


def _lighten(hex_color, factor=0.9):
    """Create a light tint of a hex colour."""
    try:
        hex_color = hex_color.lstrip("#")
        r = int(int(hex_color[0:2], 16) + (255 - int(hex_color[0:2], 16)) * factor)
        g = int(int(hex_color[2:4], 16) + (255 - int(hex_color[2:4], 16)) * factor)
        b = int(int(hex_color[4:6], 16) + (255 - int(hex_color[4:6], 16)) * factor)
        r = min(255, r)
        g = min(255, g)
        b = min(255, b)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#dcfce7"


def main():
    try:
        # Connect to database
        conn = create_connection()
        if not conn:
            print("Could not connect to database. Exiting.")
            sys.exit(1)
        conn.close()

        # Hash admin password on first run
        setup_admin_password()

        # Load and apply saved branding settings
        settings = load_saved_settings()

        # Launch app
        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        from assets.styles import app_stylesheet
        app.setStyleSheet(app_stylesheet())

        from ui.login_window import LoginWindow
        window = LoginWindow()

        # Apply saved restaurant name to window title
        if settings:
            name = settings.get(
                "restaurant_name", "Restaurant Manager"
            )
            window.setWindowTitle(name)

        window.show()
        sys.exit(app.exec())

    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()