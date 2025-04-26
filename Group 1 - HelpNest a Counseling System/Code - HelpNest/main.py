import tkinter as tk
from pages.login_page import LoginPage
from pages.register_page import RegisterPage
from pages.dashboard_junior import JuniorDashboardPage
from pages.dashboard_senior import SeniorDashboardPage
from pages.qna_page import QnAPage
from pages.settings_page import SettingsPage
from pages.leaderboard_page import LeaderboardPage
from pages.resource_sharing_page import ResourceSharingPage
from database import initialize_database
from pages.admin_dashboard import AdminDashboardPage
from pages.user_management_page import UserManagementPage
from pages.question_moderation_page import QuestionModerationPage
from pages.session_monitoring_page import SessionMonitoringPage
from pages.resource_management_page import ResourceManagementPage
from pages.leaderboard_management_page import LeaderboardManagementPage

class HelpNestApp(tk.Tk):
    def __init__(self): #constructor
        tk.Tk.__init__(self) #inherits main window tkinter tk.Tk is parent class
        self.title("Help Nest")
        self.geometry("800x600")
        # Shared variables
        self.user_id = None
        self.role = None
        self.username = None  # Add this to store the user's name

        # Container for frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Initialize the frames dictionary
        self.frames = {}

        # Dictionary to hold all frames
        for F in (
            LoginPage,
            RegisterPage,
            JuniorDashboardPage,
            SeniorDashboardPage,
            AdminDashboardPage,
            QnAPage,
            SettingsPage,
            LeaderboardPage,
            ResourceSharingPage,
            LeaderboardManagementPage,
            QuestionModerationPage,
            SessionMonitoringPage,
            ResourceManagementPage,
            UserManagementPage
        ):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the Login Page by default
        self.show_frame(LoginPage)

    def show_frame(self, page_class):
        """Show a frame for the given page class."""
        if isinstance(page_class, str):
            # Convert string to class reference
            page_class = globals().get(page_class)
            if not page_class:
                raise ValueError(f"Invalid page class: {page_class}")

        frame = self.frames[page_class]

        # Update role-specific content for the Dashboard Page
        if page_class in (JuniorDashboardPage, SeniorDashboardPage):
            if not self.role:
                raise ValueError("User role is not set.")
            if self.role == "Junior":
                frame = self.frames[JuniorDashboardPage]
            elif self.role == "Senior":
                frame = self.frames[SeniorDashboardPage]
            else:
                raise ValueError(f"Invalid role: {self.role}")

        frame.tkraise()

# Initialize the database when the application starts
initialize_database()

if __name__ == "__main__":
    app = HelpNestApp()
    app.mainloop()