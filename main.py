#!/usr/bin/env python3
"""
Main entry point for the Enhanced Desktop Billing Application with GST Support
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont
from billing_tabs.home_dashboard import HomeDashboard
from data_base.database import Database

def create_splash_screen():
    """Create a splash screen for the application"""
    splash_pixmap = QPixmap(400, 300)
    splash_pixmap.fill(Qt.white)
    
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pixmap.mask())
    
    # Add text to splash screen
    splash.showMessage("Loading Enhanced GST Billing System...", Qt.AlignCenter, Qt.black)
    
    return splash

def setup_application():
    """Setup application properties and DPI awareness"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Enhanced Desktop Billing System")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("Your Company")
    
    # Set application style for better cross-platform appearance
    app.setStyle('Fusion')
    
    return app

def main():
    """Main application entry point"""
    app = setup_application()
    
    # Create splash screen
    splash = create_splash_screen()
    splash.show()
    
    # Process events to show splash screen
    app.processEvents()
    
    try:
        # Initialize database
        splash.showMessage("Initializing database with GST support...", Qt.AlignCenter, Qt.black)
        app.processEvents()
        
        db = Database()
        
        # Create main window
        splash.showMessage("Loading main window...", Qt.AlignCenter, Qt.black)
        app.processEvents()
        
        main_window = HomeDashboard()
        
        # Show main window after a short delay
        QTimer.singleShot(1500, lambda: [splash.finish(main_window), main_window.show()])
        
    except Exception as e:
        splash.close()
        QMessageBox.critical(None, "Startup Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)
    
    # Run the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()