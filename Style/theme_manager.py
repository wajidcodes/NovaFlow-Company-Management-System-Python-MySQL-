"""
Theme Manager - Application-wide style configuration
"""
import tkinter as tk
from tkinter import ttk
from Style.config import COLORS, FONTS

class ThemeManager:
    @staticmethod
    def apply_theme(root):
        style = ttk.Style(root)
        
        # Determine theme base
        style.theme_use('clam')  # 'clam' allows more customizability than 'vista'
        
        # Treeview Styling - The key to "Modern" look
        style.configure("Treeview",
                        background="white",
                        foreground=COLORS['text_dark'],
                        fieldbackground="white",
                        rowheight=35,
                        font=(FONTS['primary'], 10),
                        borderwidth=0)
        
        style.configure("Treeview.Heading",
                        background=COLORS['bg_light'],
                        foreground=COLORS['text_muted'],
                        font=(FONTS['primary'], 10, 'bold'),
                        relief="flat")
        
        style.map("Treeview",
                  background=[('selected', COLORS['primary_light'])],
                  foreground=[('selected', COLORS['primary_dark'])])
                  
        # Scrollbar
        style.configure("Vertical.TScrollbar",
                        background=COLORS['bg_light'],
                        troughcolor="white",
                        borderwidth=0,
                        arrowsize=12)
                        
        # Combobox
        style.configure("TCombobox",
                        fieldbackground="white",
                        background="white",
                        arrowcolor=COLORS['text_muted'],
                        borderwidth=1)
                        
        # General Frame
        root.configure(bg=COLORS['bg_light'])

    @staticmethod
    def get_card_style():
        """Return generic options for a card-like frame"""
        return {
            'bg': 'white',
            'bd': 0,
            'highlightthickness': 0
            # Shadow effect is hard in pure Tkinter, simulated via borders or separate library
        }
