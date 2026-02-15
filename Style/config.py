# Style Configuration for SpaceX Company Management System
# This file contains all styling constants for the Tkinter application
# Note: Tkinter doesn't use CSS - this is a Python-based style configuration

# ============================================
# COLOR PALETTE
# ============================================

COLORS = {
    # Primary Brand Colors (Deep Blue/Indigo)
    'primary': '#4f46e5',        # Indigo 600
    'primary_hover': '#4338ca',  # Indigo 700
    'primary_light': '#e0e7ff',  # Indigo 100
    'primary_dark': '#312e81',   # Indigo 900
    
    # Backgrounds
    'bg_dark': '#0f172a',        # Slate 900
    'bg_card': 'white',
    'bg_light': '#f1f5f9',       # Slate 100
    'bg_input': '#f8fafc',       # Slate 50
    'bg_white': 'white',
    
    # Text
    'text_dark': '#1e293b',      # Slate 800
    'text_muted': '#64748b',     # Slate 500
    'text_light': '#94a3b8',     # Slate 400
    'text_white': 'white',
    
    # Semantic Colors
    'success': '#10b981',        # Emerald 500
    'success_bg': '#d1fae5',     # Emerald 100
    'warning': '#f59e0b',        # Amber 500
    'warning_bg': '#fef3c7',     # Amber 100
    'danger': '#ef4444',         # Red 500
    'danger_bg': '#fee2e2',      # Red 100
    'info': '#3b82f6',           # Blue 500
    'info_bg': '#dbeafe',        # Blue 100
    
    # Accents usually map to semantic or brand
    'accent_blue': '#60a5fa',
    'accent_purple': '#8b5cf6',
    
    # Borders
    'border': '#cbd5e1',         # Slate 300
    'border_light': '#e2e8f0',   # Slate 200
}

# ============================================
# TYPOGRAPHY
# ============================================

FONTS = {
    # Font Families
    'primary': 'Segoe UI',
    'emoji': 'Segoe UI Emoji',
    'mono': 'Courier',
    
    # Font Sizes
    'size_xs': 8,
    'size_sm': 9,
    'size_base': 10,
    'size_md': 11,
    'size_lg': 12,
    'size_xl': 13,
    'size_2xl': 16,
    'size_3xl': 24,
    'size_4xl': 32,
    'size_5xl': 36,
    'size_6xl': 48,
    
    # Font Weights
    'weight_normal': 'normal',
    'weight_bold': 'bold',
}

# ============================================
# SPACING
# ============================================

SPACING = {
    'xs': 5,
    'sm': 10,
    'md': 15,
    'lg': 20,
    'xl': 30,
    '2xl': 40,
    '3xl': 50,
}

# ============================================
# COMPONENT STYLES
# ============================================

# Button Styles
BUTTON_PRIMARY = {
    'bg': COLORS['primary'],
    'fg': COLORS['text_white'],
    'font': (FONTS['primary'], FONTS['size_xl'], FONTS['weight_bold']),
    'bd': 0,
    'cursor': 'hand2',
    'activebackground': COLORS['primary_hover'],
    'activeforeground': COLORS['text_white'],
}

BUTTON_DANGER = {
    'bg': COLORS['danger'],
    'fg': COLORS['text_white'],
    'font': (FONTS['primary'], FONTS['size_md']),
    'bd': 0,
    'cursor': 'hand2',
    'activebackground': '#dc2626',
    'activeforeground': COLORS['text_white'],
}

BUTTON_MENU = {
    'bg': COLORS['bg_white'],
    'fg': COLORS['primary'],
    'font': (FONTS['primary'], FONTS['size_md']),
    'bd': 0,
    'relief': 'flat',
    'cursor': 'hand2',
    'anchor': 'w',
}

# Label Styles
LABEL_HEADING = {
    'font': (FONTS['primary'], FONTS['size_3xl'], FONTS['weight_bold']),
    'bg': COLORS['bg_white'],
    'fg': COLORS['text_dark'],
}

LABEL_TITLE = {
    'font': (FONTS['primary'], FONTS['size_5xl'], FONTS['weight_bold']),
    'bg': COLORS['bg_card'],
    'fg': COLORS['text_white'],
}

LABEL_SUBTITLE = {
    'font': (FONTS['primary'], FONTS['size_lg']),
    'bg': COLORS['bg_card'],
    'fg': COLORS['text_muted'],
}

LABEL_FIELD = {
    'font': (FONTS['primary'], FONTS['size_md'], FONTS['weight_bold']),
    'bg': COLORS['bg_card'],
    'fg': COLORS['text_light'],
}

LABEL_INFO = {
    'font': (FONTS['primary'], FONTS['size_md']),
    'bg': COLORS['bg_white'],
    'fg': COLORS['text_muted'],
}

# Entry Styles
ENTRY_PRIMARY = {
    'font': (FONTS['primary'], FONTS['size_lg']),
    'bg': COLORS['bg_input'],
    'fg': COLORS['text_white'],
    'bd': 0,
    'insertbackground': COLORS['text_white'],
}

# Frame Styles
FRAME_CARD = {
    'bg': COLORS['bg_card'],
    'bd': 0,
}

FRAME_INPUT = {
    'bg': COLORS['bg_input'],
    'bd': 0,
    'highlightthickness': 1,
    'highlightbackground': COLORS['border'],
}

FRAME_MAIN = {
    'bg': COLORS['bg_light'],
}

FRAME_SIDEBAR = {
    'bg': COLORS['bg_white'],
}

# ============================================
# STAT CARD COLORS
# ============================================

STAT_COLORS = {
    'blue': COLORS['primary'],
    'green': COLORS['success'],
    'amber': COLORS['warning'],
    'red': COLORS['danger'],
    'purple': COLORS['info'],
}

# ============================================
# STATUS COLORS (for treeview tags)
# ============================================

STATUS_COLORS = {
    'approved': COLORS['success'],
    'rejected': COLORS['danger'],
    'pending': COLORS['bg_white'],
    'low_stock': COLORS['danger'],
    'active': COLORS['success'],
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_font(size='base', weight='normal', family='primary'):
    """Get font tuple for tkinter widgets"""
    return (FONTS[family], FONTS[f'size_{size}'], FONTS[f'weight_{weight}'])

def get_color(name):
    """Get color by name"""
    return COLORS.get(name, '#000000')

def get_spacing(size='md'):
    """Get spacing value"""
    return SPACING.get(size, 10)

# ============================================
# USAGE EXAMPLE
# ============================================
"""
To use this style configuration in your Tkinter code:

from Style.config import COLORS, FONTS, BUTTON_PRIMARY, LABEL_HEADING

# Create a button with primary style
button = tk.Button(parent, text="Login", **BUTTON_PRIMARY)

# Create a heading label
heading = tk.Label(parent, text="Dashboard", **LABEL_HEADING)

# Use individual colors
frame = tk.Frame(parent, bg=COLORS['bg_dark'])

# Use helper functions
label = tk.Label(parent, font=get_font('xl', 'bold'), fg=get_color('primary'))
"""
