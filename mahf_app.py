"""
Mahf Firmware CPU Control Panel v4.0
Professional CPU Performance & Power Management
Copyright (c) 2024-2025 Mahf Corporation
All Rights Reserved

Redesigned from scratch with Python + CustomTkinter
"""

import customtkinter as ctk
import psutil
import platform
import threading
import time
import os
import sys
import math
from tkinter import messagebox, Canvas

# ============================================================
# THEME & COLOR CONFIGURATION
# ============================================================

COLORS = {
    # Backgrounds
    "bg_main": "#0B0B1A",
    "bg_card": "#12122B",
    "bg_card_hover": "#181840",
    "bg_header": "#0E0E24",
    "bg_footer": "#0E0E24",
    "bg_inner": "#1A1A3A",
    "bg_input": "#1E1E44",

    # Accent colors
    "accent_blue": "#4A6BFF",
    "accent_blue_hover": "#6B8AFF",
    "accent_cyan": "#00D4AA",
    "accent_purple": "#6C5CE7",
    "accent_orange": "#FFA502",
    "accent_red": "#FF4757",
    "accent_green": "#00E676",
    "accent_yellow": "#FFEB3B",

    # Text
    "text_primary": "#FFFFFF",
    "text_secondary": "#A0A0C0",
    "text_muted": "#6060A0",

    # Borders
    "border": "#2A2A50",
    "border_active": "#4A6BFF",

    # Mode colors
    "mode_powersave": "#2196F3",
    "mode_balanced": "#00E676",
    "mode_performance": "#FFA502",
    "mode_extreme": "#FF4757",
}

# ============================================================
# GRADIENT CANVAS PROGRESS BAR
# ============================================================

class GradientProgressBar(Canvas):
    """Custom gradient progress bar using Canvas widget."""

    def __init__(self, master, width=200, height=10, colors=None,
                 bg_color="#1A1A3A", corner_radius=5, **kwargs):
        super().__init__(master, width=width, height=height,
                        bg=bg_color, highlightthickness=0, **kwargs)
        self.bar_width = width
        self.bar_height = height
        self.colors = colors or ["#4A6BFF", "#6C5CE7"]
        self.bg_color = bg_color
        self.corner_radius = corner_radius
        self._value = 0
        self._max_value = 100
        self._draw()

    def set(self, value):
        self._value = min(max(value, 0), self._max_value)
        self._draw()

    def configure_max(self, max_val):
        self._max_value = max_val

    def _draw(self):
        self.delete("all")
        w = self.bar_width
        h = self.bar_height
        r = self.corner_radius

        # Background track
        self._rounded_rect(0, 0, w, h, r, "#0D0D20")

        # Filled portion
        if self._value > 0 and self._max_value > 0:
            fill_w = max(int((self._value / self._max_value) * w), r * 2)
            fill_w = min(fill_w, w)

            # Draw gradient segments
            steps = max(fill_w, 1)
            for i in range(steps):
                ratio = i / max(w - 1, 1)
                color = self._interpolate_color(ratio)
                x = i
                self.create_line(x, 2, x, h - 2, fill=color, width=1)

            # Round the edges by overlaying
            self._rounded_rect_outline(0, 0, fill_w, h, r)

    def _interpolate_color(self, ratio):
        if len(self.colors) < 2:
            return self.colors[0]

        segment = ratio * (len(self.colors) - 1)
        idx = int(segment)
        idx = min(idx, len(self.colors) - 2)
        local_ratio = segment - idx

        c1 = self._hex_to_rgb(self.colors[idx])
        c2 = self._hex_to_rgb(self.colors[idx + 1])

        r = int(c1[0] + (c2[0] - c1[0]) * local_ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * local_ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * local_ratio)

        return f"#{r:02x}{g:02x}{b:02x}"

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rounded_rect(self, x1, y1, x2, y2, r, color):
        self.create_rectangle(x1, y1, x2, y2, fill=color, outline="", width=0)

    def _rounded_rect_outline(self, x1, y1, x2, y2, r):
        pass  # Visual overlay handled by gradient draw


# ============================================================
# CIRCULAR GAUGE WIDGET
# ============================================================

class CircularGauge(Canvas):
    """Circular gauge for CPU usage display."""

    def __init__(self, master, size=120, thickness=10,
                 colors=None, bg_color="#12122B", **kwargs):
        super().__init__(master, width=size, height=size,
                        bg=bg_color, highlightthickness=0, **kwargs)
        self.size = size
        self.thickness = thickness
        self.colors = colors or ["#4A6BFF", "#6C5CE7", "#FF4757"]
        self.bg_color = bg_color
        self._value = 0
        self._text = "0%"
        self._draw()

    def set(self, value, text=None):
        self._value = min(max(value, 0), 100)
        self._text = text or f"{int(self._value)}%"
        self._draw()

    def _draw(self):
        self.delete("all")
        s = self.size
        t = self.thickness
        pad = t + 4
        cx, cy = s // 2, s // 2

        # Background arc (full circle)
        self.create_arc(pad, pad, s - pad, s - pad,
                       start=90, extent=-360,
                       style="arc", outline="#1A1A3A", width=t)

        # Value arc
        if self._value > 0:
            extent = -(self._value / 100) * 360
            ratio = self._value / 100
            color = self._get_color(ratio)
            self.create_arc(pad, pad, s - pad, s - pad,
                           start=90, extent=extent,
                           style="arc", outline=color, width=t)

            # Glow effect
            glow_color = color + "40" if len(color) == 7 else color
            self.create_arc(pad - 2, pad - 2, s - pad + 2, s - pad + 2,
                           start=90, extent=extent,
                           style="arc", outline=color, width=1)

        # Center text
        self.create_text(cx, cy - 6, text=self._text,
                        fill="#FFFFFF", font=("Segoe UI", 18, "bold"))
        self.create_text(cx, cy + 16, text="CPU",
                        fill="#6060A0", font=("Segoe UI", 9))

    def _get_color(self, ratio):
        if ratio < 0.5:
            return self._interpolate(self.colors[0], self.colors[1], ratio * 2)
        else:
            return self._interpolate(self.colors[1], self.colors[2], (ratio - 0.5) * 2)

    def _interpolate(self, c1, c2, ratio):
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# ============================================================
# MAIN APPLICATION
# ============================================================

class MahfControlPanel(ctk.CTk):
    """Main Mahf CPU Control Panel Application."""

    VERSION = "4.0.0"
    APP_NAME = "Mahf Firmware CPU Control Panel"

    def __init__(self):
        super().__init__()

        # Window setup
        self.title(f"{self.APP_NAME} v{self.VERSION}")
        self.geometry("1050x720")
        self.minsize(900, 650)
        self.configure(fg_color=COLORS["bg_main"])

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State
        self.current_mode = "Balanced"
        self.is_running = True
        self.driver_connected = True  # Simulated
        self.cpu_history = []

        # Get CPU info
        self._detect_cpu()

        # Build UI
        self._build_header()
        self._build_main_content()
        self._build_footer()

        # Start monitoring
        self._start_monitoring()

        # Center window
        self.update_idletasks()
        self._center_window()

    def _detect_cpu(self):
        """Detect CPU information using psutil and platform."""
        self.cpu_name = platform.processor() or "Unknown CPU"

        # Try to get a better CPU name
        try:
            import subprocess
            result = subprocess.run(
                ["wmic", "cpu", "get", "name"],
                capture_output=True, text=True, timeout=5
            )
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            if len(lines) > 1:
                self.cpu_name = lines[1]
        except Exception:
            pass

        self.cpu_cores = psutil.cpu_count(logical=False) or 4
        self.cpu_threads = psutil.cpu_count(logical=True) or 8

        # Frequency info
        freq = psutil.cpu_freq()
        if freq:
            self.base_freq = int(freq.min) if freq.min else int(freq.current)
            self.max_freq = int(freq.max) if freq.max else int(freq.current)
            if self.base_freq == 0:
                self.base_freq = int(freq.current)
            if self.max_freq == 0:
                self.max_freq = int(freq.current)
        else:
            self.base_freq = 3000
            self.max_freq = 4500

        # Detect vendor
        cpu_lower = self.cpu_name.lower()
        if "intel" in cpu_lower:
            self.cpu_vendor = "Intel"
        elif "amd" in cpu_lower:
            self.cpu_vendor = "AMD"
        else:
            self.cpu_vendor = "Unknown"

    def _center_window(self):
        """Center the window on screen."""
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"+{x}+{y}")

    # ============================================================
    # HEADER
    # ============================================================

    def _build_header(self):
        """Build the header section."""
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_header"],
                             corner_radius=0, height=80)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        # Title container
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo/Icon text
        logo_label = ctk.CTkLabel(
            title_frame, text="⚡",
            font=("Segoe UI", 32),
            text_color=COLORS["accent_blue"]
        )
        logo_label.pack(side="left", padx=(0, 12))

        # Title text frame
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left")

        title = ctk.CTkLabel(
            text_frame, text="MAHF FIRMWARE CPU DRIVER",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["accent_blue"]
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            text_frame,
            text="Professional Universal CPU Performance Management",
            font=("Segoe UI", 12),
            text_color=COLORS["text_secondary"]
        )
        subtitle.pack(anchor="w")

        # Version badge
        version_badge = ctk.CTkLabel(
            header, text=f"v{self.VERSION}",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["accent_cyan"],
            fg_color=COLORS["bg_inner"],
            corner_radius=8,
            padx=10, pady=2
        )
        version_badge.place(relx=0.97, rely=0.5, anchor="e")

    # ============================================================
    # MAIN CONTENT
    # ============================================================

    def _build_main_content(self):
        """Build the main content area."""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=(12, 8))

        # Left panel (System Info)
        self._build_left_panel(content)

        # Right panel (Monitoring + Controls)
        self._build_right_panel(content)

    def _build_left_panel(self, parent):
        """Build the left panel with system information."""
        left = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                           corner_radius=12, width=280,
                           border_width=1, border_color=COLORS["border"])
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        # Section title
        section_title = ctk.CTkLabel(
            left, text="⚙  SYSTEM INFORMATION",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["accent_cyan"]
        )
        section_title.pack(anchor="w", padx=16, pady=(16, 12))

        # Separator
        sep = ctk.CTkFrame(left, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=16, pady=(0, 12))

        # CPU Info Card
        cpu_card = ctk.CTkFrame(left, fg_color=COLORS["bg_inner"],
                               corner_radius=10)
        cpu_card.pack(fill="x", padx=12, pady=(0, 8))

        # Vendor icon
        vendor_icon = "🔵" if self.cpu_vendor == "Intel" else "🔴" if self.cpu_vendor == "AMD" else "⚪"
        vendor_label = ctk.CTkLabel(
            cpu_card, text=f"{vendor_icon} {self.cpu_vendor}",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["text_primary"]
        )
        vendor_label.pack(padx=12, pady=(12, 4))

        # CPU Name
        cpu_name_label = ctk.CTkLabel(
            cpu_card, text=self.cpu_name,
            font=("Segoe UI", 11),
            text_color=COLORS["text_secondary"],
            wraplength=240
        )
        cpu_name_label.pack(padx=12, pady=(0, 4))

        # Cores/Threads
        cores_label = ctk.CTkLabel(
            cpu_card,
            text=f"{self.cpu_cores} Cores / {self.cpu_threads} Threads",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["accent_purple"]
        )
        cores_label.pack(padx=12, pady=(0, 12))

        # Frequency Card
        freq_card = ctk.CTkFrame(left, fg_color=COLORS["bg_inner"],
                                corner_radius=10)
        freq_card.pack(fill="x", padx=12, pady=(4, 8))

        freq_title = ctk.CTkLabel(
            freq_card, text="FREQUENCY",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_muted"]
        )
        freq_title.pack(anchor="w", padx=12, pady=(10, 4))

        self.base_freq_label = ctk.CTkLabel(
            freq_card,
            text=f"⚡ Base: {self.base_freq} MHz",
            font=("Segoe UI", 12),
            text_color=COLORS["text_primary"]
        )
        self.base_freq_label.pack(anchor="w", padx=12, pady=(0, 2))

        self.max_freq_label = ctk.CTkLabel(
            freq_card,
            text=f"🚀 Max: {self.max_freq} MHz",
            font=("Segoe UI", 12),
            text_color=COLORS["accent_orange"]
        )
        self.max_freq_label.pack(anchor="w", padx=12, pady=(0, 10))

        # Architecture Info
        arch_card = ctk.CTkFrame(left, fg_color=COLORS["bg_inner"],
                                corner_radius=10)
        arch_card.pack(fill="x", padx=12, pady=(4, 8))

        arch_title = ctk.CTkLabel(
            arch_card, text="ARCHITECTURE",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_muted"]
        )
        arch_title.pack(anchor="w", padx=12, pady=(10, 4))

        arch_val = ctk.CTkLabel(
            arch_card,
            text=f"📐 {platform.machine()} ({platform.architecture()[0]})",
            font=("Segoe UI", 12),
            text_color=COLORS["text_primary"]
        )
        arch_val.pack(anchor="w", padx=12, pady=(0, 2))

        os_val = ctk.CTkLabel(
            arch_card,
            text=f"💻 {platform.system()} {platform.release()}",
            font=("Segoe UI", 12),
            text_color=COLORS["text_primary"]
        )
        os_val.pack(anchor="w", padx=12, pady=(0, 10))

        # Driver Status Card
        status_card = ctk.CTkFrame(left, fg_color=COLORS["bg_inner"],
                                  corner_radius=10)
        status_card.pack(fill="x", padx=12, pady=(4, 8))

        status_title = ctk.CTkLabel(
            status_card, text="DRIVER STATUS",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_muted"]
        )
        status_title.pack(anchor="w", padx=12, pady=(10, 4))

        status_row = ctk.CTkFrame(status_card, fg_color="transparent")
        status_row.pack(anchor="w", padx=12, pady=(0, 4))

        self.status_dot = ctk.CTkLabel(
            status_row, text="●",
            font=("Segoe UI", 14),
            text_color=COLORS["accent_green"]
        )
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_label = ctk.CTkLabel(
            status_row, text="Connected",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["accent_green"]
        )
        self.status_label.pack(side="left")

        # Refresh button
        refresh_btn = ctk.CTkButton(
            status_card, text="🔄 Refresh Connection",
            font=("Segoe UI", 11),
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["accent_blue"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=8,
            height=32,
            command=self._refresh_connection
        )
        refresh_btn.pack(fill="x", padx=12, pady=(4, 12))

    def _build_right_panel(self, parent):
        """Build the right panel with monitoring and controls."""
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True)

        # Top section - Monitoring Cards
        self._build_monitoring_section(right)

        # Bottom section - Performance Modes
        self._build_performance_section(right)

    def _build_monitoring_section(self, parent):
        """Build the real-time monitoring section."""
        monitor_frame = ctk.CTkFrame(parent, fg_color="transparent")
        monitor_frame.pack(fill="x", pady=(0, 8))

        cards_data = [
            {
                "title": "CPU USAGE",
                "icon": "📊",
                "value_attr": "cpu_usage_label",
                "bar_attr": "cpu_usage_bar",
                "colors": [COLORS["accent_blue"], COLORS["accent_purple"]],
                "default": "0%",
                "accent": COLORS["accent_blue"]
            },
            {
                "title": "TEMPERATURE",
                "icon": "🌡️",
                "value_attr": "temp_label",
                "bar_attr": "temp_bar",
                "colors": [COLORS["accent_cyan"], COLORS["accent_orange"], COLORS["accent_red"]],
                "default": "0°C",
                "accent": COLORS["accent_cyan"]
            },
            {
                "title": "POWER",
                "icon": "⚡",
                "value_attr": "power_label",
                "bar_attr": "power_bar",
                "colors": [COLORS["accent_orange"], COLORS["accent_red"]],
                "default": "0W",
                "accent": COLORS["accent_orange"],
                "max": 150
            },
            {
                "title": "FREQUENCY",
                "icon": "📡",
                "value_attr": "freq_label",
                "bar_attr": None,
                "colors": [],
                "default": "0 MHz",
                "accent": COLORS["accent_purple"],
                "extra_attr": "voltage_label"
            }
        ]

        for i, card_info in enumerate(cards_data):
            card = ctk.CTkFrame(monitor_frame, fg_color=COLORS["bg_card"],
                               corner_radius=12, border_width=1,
                               border_color=COLORS["border"])
            card.pack(side="left", fill="both", expand=True,
                     padx=(0 if i == 0 else 4, 0 if i == len(cards_data)-1 else 4))

            # Title row
            title_row = ctk.CTkFrame(card, fg_color="transparent")
            title_row.pack(fill="x", padx=14, pady=(14, 0))

            icon_label = ctk.CTkLabel(
                title_row, text=card_info["icon"],
                font=("Segoe UI", 14)
            )
            icon_label.pack(side="left", padx=(0, 6))

            title_label = ctk.CTkLabel(
                title_row, text=card_info["title"],
                font=("Segoe UI", 10, "bold"),
                text_color=COLORS["text_muted"]
            )
            title_label.pack(side="left")

            # Value
            value_label = ctk.CTkLabel(
                card, text=card_info["default"],
                font=("Segoe UI", 28, "bold"),
                text_color=card_info["accent"]
            )
            value_label.pack(padx=14, pady=(8, 4))
            setattr(self, card_info["value_attr"], value_label)

            # Progress bar
            if card_info["bar_attr"]:
                bar = GradientProgressBar(
                    card, width=150, height=8,
                    colors=card_info["colors"],
                    bg_color=COLORS["bg_card"]
                )
                bar.pack(padx=14, pady=(0, 14))
                if "max" in card_info:
                    bar.configure_max(card_info["max"])
                setattr(self, card_info["bar_attr"], bar)

            # Extra label (voltage)
            if "extra_attr" in card_info:
                extra = ctk.CTkLabel(
                    card, text="0.00V",
                    font=("Segoe UI", 13),
                    text_color=COLORS["text_secondary"]
                )
                extra.pack(pady=(0, 14))
                setattr(self, card_info["extra_attr"], extra)

    def _build_performance_section(self, parent):
        """Build the performance mode selection section."""
        perf_card = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"],
                                corner_radius=12, border_width=1,
                                border_color=COLORS["border"])
        perf_card.pack(fill="both", expand=True)

        # Title row
        title_row = ctk.CTkFrame(perf_card, fg_color="transparent")
        title_row.pack(fill="x", padx=20, pady=(16, 0))

        perf_title = ctk.CTkLabel(
            title_row, text="🎮  PERFORMANCE MODES",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["accent_cyan"]
        )
        perf_title.pack(side="left")

        # Current mode indicator
        mode_indicator_frame = ctk.CTkFrame(
            title_row, fg_color=COLORS["bg_inner"],
            corner_radius=8
        )
        mode_indicator_frame.pack(side="right")

        current_label = ctk.CTkLabel(
            mode_indicator_frame, text="CURRENT:",
            font=("Segoe UI", 10, "bold"),
            text_color=COLORS["text_muted"]
        )
        current_label.pack(side="left", padx=(10, 4), pady=6)

        self.current_mode_dot = ctk.CTkLabel(
            mode_indicator_frame, text="●",
            font=("Segoe UI", 12),
            text_color=COLORS["mode_balanced"]
        )
        self.current_mode_dot.pack(side="left", padx=(0, 4))

        self.current_mode_label = ctk.CTkLabel(
            mode_indicator_frame, text="Balanced",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text_primary"]
        )
        self.current_mode_label.pack(side="left", padx=(0, 10), pady=6)

        # Separator
        sep = ctk.CTkFrame(perf_card, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=(12, 16))

        # CPU Gauge + Mode Buttons row
        main_row = ctk.CTkFrame(perf_card, fg_color="transparent")
        main_row.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Circular Gauge (left)
        gauge_frame = ctk.CTkFrame(main_row, fg_color=COLORS["bg_inner"],
                                   corner_radius=12, width=160)
        gauge_frame.pack(side="left", fill="y", padx=(0, 16))
        gauge_frame.pack_propagate(False)

        self.cpu_gauge = CircularGauge(
            gauge_frame, size=130, thickness=10,
            colors=[COLORS["accent_blue"], COLORS["accent_purple"], COLORS["accent_red"]],
            bg_color=COLORS["bg_inner"]
        )
        self.cpu_gauge.pack(expand=True)

        # Mode Buttons (right)
        buttons_frame = ctk.CTkFrame(main_row, fg_color="transparent")
        buttons_frame.pack(side="left", fill="both", expand=True)

        modes = [
            {
                "name": "POWER SAVE",
                "desc": "Maximum Efficiency • Low Power",
                "icon": "🔋",
                "color": COLORS["mode_powersave"],
                "mode": "Power Save"
            },
            {
                "name": "BALANCED",
                "desc": "Optimal Balance • Recommended",
                "icon": "⚖️",
                "color": COLORS["mode_balanced"],
                "mode": "Balanced"
            },
            {
                "name": "PERFORMANCE",
                "desc": "High Performance • Higher Power",
                "icon": "🚀",
                "color": COLORS["mode_performance"],
                "mode": "Performance"
            },
            {
                "name": "EXTREME",
                "desc": "Maximum Power • High Heat",
                "icon": "🔥",
                "color": COLORS["mode_extreme"],
                "mode": "Extreme"
            }
        ]

        # 2x2 grid for mode buttons
        top_row = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        top_row.pack(fill="both", expand=True, pady=(0, 4))

        bottom_row = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        bottom_row.pack(fill="both", expand=True, pady=(4, 0))

        rows = [top_row, top_row, bottom_row, bottom_row]
        self.mode_buttons = {}

        for i, mode_info in enumerate(modes):
            row_frame = rows[i]

            btn_frame = ctk.CTkFrame(row_frame, fg_color=COLORS["bg_inner"],
                                    corner_radius=10, border_width=2,
                                    border_color=COLORS["border"],
                                    cursor="hand2")
            btn_frame.pack(side="left", fill="both", expand=True,
                          padx=(0 if i % 2 == 0 else 4, 4 if i % 2 == 0 else 0))

            # Make the whole frame clickable
            mode_key = mode_info["mode"]

            # Icon + Name
            icon_name_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
            icon_name_frame.pack(expand=True)

            icon = ctk.CTkLabel(
                icon_name_frame, text=mode_info["icon"],
                font=("Segoe UI", 20)
            )
            icon.pack(pady=(8, 2))

            name = ctk.CTkLabel(
                icon_name_frame, text=mode_info["name"],
                font=("Segoe UI", 14, "bold"),
                text_color=COLORS["text_primary"]
            )
            name.pack()

            desc = ctk.CTkLabel(
                icon_name_frame, text=mode_info["desc"],
                font=("Segoe UI", 9),
                text_color=COLORS["text_muted"]
            )
            desc.pack(pady=(0, 8))

            self.mode_buttons[mode_key] = btn_frame

            # Bind click events to all children
            def make_click_handler(m=mode_key):
                return lambda e: self._set_mode(m)

            def make_enter_handler(f=btn_frame, c=mode_info["color"]):
                return lambda e: f.configure(border_color=c)

            def make_leave_handler(f=btn_frame, m=mode_key):
                return lambda e: f.configure(
                    border_color=COLORS["border"] if m != self.current_mode else self._get_mode_color(m))

            for widget in [btn_frame, icon_name_frame, icon, name, desc]:
                widget.bind("<Button-1>", make_click_handler())
                widget.bind("<Enter>", make_enter_handler())
                widget.bind("<Leave>", make_leave_handler())

        # Highlight default mode
        self._update_mode_buttons()

    # ============================================================
    # FOOTER
    # ============================================================

    def _build_footer(self):
        """Build the footer section."""
        footer = ctk.CTkFrame(self, fg_color=COLORS["bg_footer"],
                             corner_radius=0, height=50)
        footer.pack(fill="x")
        footer.pack_propagate(False)

        # Status message (left)
        self.status_message = ctk.CTkLabel(
            footer, text="",
            font=("Segoe UI", 11),
            text_color=COLORS["text_secondary"]
        )
        self.status_message.pack(side="left", padx=16)

        # Buttons (right)
        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(side="right", padx=12)

        buttons = [
            ("⚙ Settings", self._show_settings),
            ("ℹ About", self._show_about),
            ("✕ Exit", self._exit_app)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(
                btn_frame, text=text,
                font=("Segoe UI", 11),
                fg_color="transparent",
                hover_color=COLORS["accent_blue"],
                border_width=1,
                border_color=COLORS["border"],
                corner_radius=8,
                width=90, height=32,
                command=command
            )
            btn.pack(side="left", padx=3)

    # ============================================================
    # MONITORING
    # ============================================================

    def _start_monitoring(self):
        """Start the monitoring thread."""
        self._update_data()

    def _update_data(self):
        """Update monitoring data periodically."""
        if not self.is_running:
            return

        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=0)
            self.cpu_usage_label.configure(text=f"{cpu_percent:.0f}%")
            self.cpu_usage_bar.set(cpu_percent)
            self.cpu_gauge.set(cpu_percent, f"{cpu_percent:.0f}%")

            # Temperature (estimate based on usage if not available)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            temp = entries[0].current
                            break
                    else:
                        temp = 40 + cpu_percent * 0.5
                else:
                    temp = 40 + cpu_percent * 0.5
            except (AttributeError, Exception):
                # sensors_temperatures not available on Windows typically
                temp = 35 + cpu_percent * 0.45 + (5 if self.current_mode == "Performance" else
                       10 if self.current_mode == "Extreme" else 0)

            self.temp_label.configure(text=f"{temp:.0f}°C")
            self.temp_bar.set(temp)

            # Frequency
            freq = psutil.cpu_freq()
            if freq:
                current_freq = int(freq.current)
                self.freq_label.configure(text=f"{current_freq} MHz")

                # Estimate voltage based on frequency ratio
                if self.max_freq > 0:
                    ratio = current_freq / max(self.max_freq, 1)
                else:
                    ratio = 0.8
                voltage = 0.8 + ratio * 0.5
                self.voltage_label.configure(text=f"{voltage:.2f}V")
            else:
                self.freq_label.configure(text=f"{self.base_freq} MHz")
                self.voltage_label.configure(text="1.10V")

            # Power (estimate: TDP * usage ratio)
            base_tdp = self.cpu_cores * 10  # rough estimate
            mode_multiplier = {
                "Power Save": 0.5,
                "Balanced": 0.75,
                "Performance": 1.0,
                "Extreme": 1.3
            }.get(self.current_mode, 0.75)
            power = base_tdp * (cpu_percent / 100) * mode_multiplier
            power = max(power, 5)  # minimum idle power
            self.power_label.configure(text=f"{power:.0f}W")
            self.power_bar.set(power)

            # Update title
            self.title(
                f"{self.APP_NAME} — {cpu_percent:.0f}% CPU • {temp:.0f}°C"
            )

        except Exception as e:
            pass

        # Schedule next update
        if self.is_running:
            self.after(1000, self._update_data)

    # ============================================================
    # MODE MANAGEMENT
    # ============================================================

    def _set_mode(self, mode):
        """Set the performance mode."""
        if mode == "Extreme":
            result = messagebox.askyesno(
                "⚠ Extreme Mode Warning",
                "Extreme mode may significantly increase:\n\n"
                "• CPU temperature\n"
                "• Power consumption\n"
                "• Fan noise\n\n"
                "This could reduce hardware lifespan.\n\n"
                "Continue with Extreme mode?",
                icon="warning"
            )
            if not result:
                return

        self.current_mode = mode
        self._update_mode_buttons()

        # Update indicator
        color = self._get_mode_color(mode)
        self.current_mode_dot.configure(text_color=color)
        self.current_mode_label.configure(text=mode)

        # Status message
        self._show_status(f"✓ Performance mode set to: {mode}", COLORS["accent_green"])

    def _get_mode_color(self, mode):
        """Get color for a performance mode."""
        return {
            "Power Save": COLORS["mode_powersave"],
            "Balanced": COLORS["mode_balanced"],
            "Performance": COLORS["mode_performance"],
            "Extreme": COLORS["mode_extreme"]
        }.get(mode, COLORS["accent_blue"])

    def _update_mode_buttons(self):
        """Update mode button visual states."""
        for mode, btn_frame in self.mode_buttons.items():
            if mode == self.current_mode:
                color = self._get_mode_color(mode)
                btn_frame.configure(
                    border_color=color,
                    fg_color=self._darken_color(color, 0.15)
                )
            else:
                btn_frame.configure(
                    border_color=COLORS["border"],
                    fg_color=COLORS["bg_inner"]
                )

    def _darken_color(self, hex_color, factor):
        """Darken a hex color by a factor."""
        hex_color = hex_color.lstrip('#')
        r = int(int(hex_color[0:2], 16) * factor)
        g = int(int(hex_color[2:4], 16) * factor)
        b = int(int(hex_color[4:6], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"

    # ============================================================
    # DIALOGS
    # ============================================================

    def _refresh_connection(self):
        """Refresh driver connection."""
        self.status_dot.configure(text_color=COLORS["accent_orange"])
        self.status_label.configure(
            text="Reconnecting...",
            text_color=COLORS["accent_orange"]
        )
        self._show_status("🔄 Refreshing driver connection...", COLORS["accent_orange"])

        # Simulate reconnection
        def reconnect():
            time.sleep(1)
            self.after(0, self._complete_reconnect)

        threading.Thread(target=reconnect, daemon=True).start()

    def _complete_reconnect(self):
        """Complete the reconnection process."""
        self.driver_connected = True
        self.status_dot.configure(text_color=COLORS["accent_green"])
        self.status_label.configure(
            text="Connected",
            text_color=COLORS["accent_green"]
        )
        self._show_status("✓ Driver connection refreshed successfully", COLORS["accent_green"])

    def _show_settings(self):
        """Show settings dialog."""
        settings_win = ctk.CTkToplevel(self)
        settings_win.title("Settings")
        settings_win.geometry("450x500")
        settings_win.configure(fg_color=COLORS["bg_main"])
        settings_win.transient(self)
        settings_win.grab_set()

        # Center on parent
        settings_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 450) // 2
        y = self.winfo_y() + (self.winfo_height() - 500) // 2
        settings_win.geometry(f"+{x}+{y}")

        # Title
        title = ctk.CTkLabel(
            settings_win, text="⚙  Settings",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["accent_blue"]
        )
        title.pack(padx=20, pady=(20, 16))

        sep = ctk.CTkFrame(settings_win, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=(0, 16))

        # Settings options
        settings_frame = ctk.CTkFrame(settings_win, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True, padx=20)

        # Auto-start
        autostart_var = ctk.BooleanVar(value=False)
        autostart = ctk.CTkSwitch(
            settings_frame, text="Start with Windows",
            font=("Segoe UI", 13),
            variable=autostart_var,
            progress_color=COLORS["accent_blue"]
        )
        autostart.pack(anchor="w", pady=8)

        # Start minimized
        minimize_var = ctk.BooleanVar(value=False)
        minimize = ctk.CTkSwitch(
            settings_frame, text="Start minimized to tray",
            font=("Segoe UI", 13),
            variable=minimize_var,
            progress_color=COLORS["accent_blue"]
        )
        minimize.pack(anchor="w", pady=8)

        # Update interval
        interval_label = ctk.CTkLabel(
            settings_frame, text="Update Interval",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_secondary"]
        )
        interval_label.pack(anchor="w", pady=(16, 4))

        interval_slider = ctk.CTkSlider(
            settings_frame, from_=500, to=5000,
            number_of_steps=9,
            progress_color=COLORS["accent_blue"],
            button_color=COLORS["accent_blue"],
            button_hover_color=COLORS["accent_blue_hover"]
        )
        interval_slider.set(1000)
        interval_slider.pack(fill="x", pady=4)

        interval_val = ctk.CTkLabel(
            settings_frame, text="1000ms",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"]
        )
        interval_val.pack(anchor="w")

        def update_interval_label(val):
            interval_val.configure(text=f"{int(val)}ms")

        interval_slider.configure(command=update_interval_label)

        # Thermal limit
        thermal_label = ctk.CTkLabel(
            settings_frame, text="Thermal Limit (°C)",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text_secondary"]
        )
        thermal_label.pack(anchor="w", pady=(16, 4))

        thermal_slider = ctk.CTkSlider(
            settings_frame, from_=60, to=100,
            number_of_steps=8,
            progress_color=COLORS["accent_orange"],
            button_color=COLORS["accent_orange"],
            button_hover_color=COLORS["accent_red"]
        )
        thermal_slider.set(85)
        thermal_slider.pack(fill="x", pady=4)

        thermal_val = ctk.CTkLabel(
            settings_frame, text="85°C",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"]
        )
        thermal_val.pack(anchor="w")

        def update_thermal_label(val):
            thermal_val.configure(text=f"{int(val)}°C")

        thermal_slider.configure(command=update_thermal_label)

        # Close button
        close_btn = ctk.CTkButton(
            settings_win, text="Close",
            font=("Segoe UI", 13),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_hover"],
            corner_radius=8,
            height=36,
            command=settings_win.destroy
        )
        close_btn.pack(pady=16)

    def _show_about(self):
        """Show about dialog."""
        about_win = ctk.CTkToplevel(self)
        about_win.title("About")
        about_win.geometry("400x420")
        about_win.configure(fg_color=COLORS["bg_main"])
        about_win.transient(self)
        about_win.grab_set()
        about_win.resizable(False, False)

        # Center on parent
        about_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 420) // 2
        about_win.geometry(f"+{x}+{y}")

        # Logo
        logo = ctk.CTkLabel(
            about_win, text="⚡",
            font=("Segoe UI", 48)
        )
        logo.pack(pady=(30, 10))

        # Title
        title = ctk.CTkLabel(
            about_win, text="Mahf Firmware CPU Driver",
            font=("Segoe UI", 20, "bold"),
            text_color=COLORS["accent_blue"]
        )
        title.pack()

        # Version
        version = ctk.CTkLabel(
            about_win, text=f"Version {self.VERSION}",
            font=("Segoe UI", 14),
            text_color=COLORS["accent_cyan"]
        )
        version.pack(pady=(4, 16))

        sep = ctk.CTkFrame(about_win, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=40)

        # Info
        info_text = (
            "Professional Universal CPU Performance\n"
            "and Power Management System\n\n"
            f"Supports: Intel, AMD Architectures\n"
            f"Platform: {platform.system()} {platform.release()}\n"
            f"Python: {platform.python_version()}"
        )
        info = ctk.CTkLabel(
            about_win, text=info_text,
            font=("Segoe UI", 12),
            text_color=COLORS["text_secondary"],
            justify="center"
        )
        info.pack(pady=16)

        # Copyright
        copyright = ctk.CTkLabel(
            about_win,
            text="Copyright © 2024-2025 Mahf Corporation\nAll Rights Reserved",
            font=("Segoe UI", 11),
            text_color=COLORS["text_muted"],
            justify="center"
        )
        copyright.pack(pady=(0, 16))

        # Close button
        close_btn = ctk.CTkButton(
            about_win, text="Close",
            font=("Segoe UI", 13),
            fg_color=COLORS["accent_blue"],
            hover_color=COLORS["accent_blue_hover"],
            corner_radius=8,
            width=120, height=36,
            command=about_win.destroy
        )
        close_btn.pack(pady=(0, 20))

    def _show_status(self, message, color=None):
        """Show a status message in the footer."""
        self.status_message.configure(
            text=message,
            text_color=color or COLORS["text_secondary"]
        )
        # Auto-clear after 4 seconds
        self.after(4000, lambda: self.status_message.configure(text=""))

    def _exit_app(self):
        """Exit the application."""
        self.is_running = False
        self.destroy()

    def destroy(self):
        """Override destroy to clean up."""
        self.is_running = False
        super().destroy()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = MahfControlPanel()
    app.mainloop()
