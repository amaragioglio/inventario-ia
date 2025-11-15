"""
Sistema de gestión de temas (Dark/Light/Auto) con detección del sistema operativo
"""

import tkinter as tk
from tkinter import ttk
import platform
import subprocess
import json
import os

class ThemeManager:
    """Gestiona los temas de la aplicación"""

    # TEMA CLARO (Light Mode)
    LIGHT = {
        'name': 'light',
        'bg': '#F5F5F7',
        'panel': '#FFFFFF',
        'text': '#1C1C1E',
        'text_secondary': '#6E6E73',
        'border': '#D1D1D6',
        'shadow': '#E5E5EA',
        'primary': '#0A84FF',
        'success': '#30D158',
        'warning': '#FFD60A',
        'danger': '#FF3B30',
        'info': '#5E5CE6',
        'chart_bg': '#FFFFFF',
        'hover': '#F0F0F2',
        'accent': '#FF9F0A',
        'card_bg': '#FAFAFA',
        'input_bg': '#FFFFFF',
        'tree_header': '#E5E5EA',
        'tree_selected': '#D1E7FF',
        'tree_odd_row': '#FFFFFF',
        'tree_even_row': '#FBFBFD',
    }

    # TEMA OSCURO (Dark Mode)
    DARK = {
        'name': 'dark',
        'bg': '#1C1C1E',
        'panel': '#2C2C2E',
        'text': '#FFFFFF',
        'text_secondary': '#98989D',
        'border': '#38383A',
        'shadow': '#000000',
        'primary': '#0A84FF',
        'success': '#30D158',
        'warning': '#FFD60A',
        'danger': '#FF453A',
        'info': '#5E5CE6',
        'chart_bg': '#2C2C2E',
        'hover': '#3A3A3C',
        'accent': '#FF9F0A',
        'card_bg': '#38383A',
        'input_bg': '#3A3A3C',
        'tree_header': '#38383A',
        'tree_selected': '#0A4D8C',
        'tree_odd_row': '#2C2C2E',
        'tree_even_row': '#3A3A3C',
    }

    def __init__(self, config_file='theme_config.json'):
        self.config_file = config_file
        self.current_theme = self.LIGHT
        self.mode = 'auto'  # 'light', 'dark', 'auto'
        self.callbacks = []

        # Cargar configuración guardada
        self.load_config()

        # Aplicar tema inicial
        self.apply_theme()

    def load_config(self):
        """Carga la configuración del tema desde archivo"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.mode = config.get('mode', 'auto')
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            self.mode = 'auto'

    def save_config(self):
        """Guarda la configuración del tema"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'mode': self.mode}, f)
        except Exception as e:
            print(f"Error guardando configuración: {e}")

    def detect_system_theme(self):
        """Detecta el tema del sistema operativo"""
        system = platform.system()

        try:
            if system == 'Windows':
                return self._detect_windows_theme()
            elif system == 'Darwin':  # macOS
                return self._detect_macos_theme()
            elif system == 'Linux':
                return self._detect_linux_theme()
        except Exception as e:
            print(f"Error detectando tema del sistema: {e}")

        return 'light'  # Por defecto

    def _detect_windows_theme(self):
        """Detecta el tema en Windows"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            winreg.CloseKey(key)
            return 'light' if value == 1 else 'dark'
        except:
            return 'light'

    def _detect_macos_theme(self):
        """Detecta el tema en macOS"""
        try:
            result = subprocess.run(
                ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                capture_output=True,
                text=True
            )
            return 'dark' if 'Dark' in result.stdout else 'light'
        except:
            return 'light'

    def _detect_linux_theme(self):
        """Detecta el tema en Linux"""
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'],
                capture_output=True,
                text=True
            )
            theme = result.stdout.strip().lower()
            return 'dark' if 'dark' in theme else 'light'
        except:
            return 'light'

    def set_mode(self, mode):
        """Cambia el modo del tema ('light', 'dark', 'auto')"""
        if mode not in ['light', 'dark', 'auto']:
            return

        self.mode = mode
        self.save_config()
        self.apply_theme()

        # Notificar a callbacks
        self.notify_callbacks()

    def apply_theme(self):
        """Aplica el tema según el modo actual"""
        if self.mode == 'auto':
            system_theme = self.detect_system_theme()
            self.current_theme = self.DARK if system_theme == 'dark' else self.LIGHT
        elif self.mode == 'dark':
            self.current_theme = self.DARK
        else:
            self.current_theme = self.LIGHT

    def get_color(self, key):
        """Obtiene un color del tema actual"""
        return self.current_theme.get(key, '#000000')

    def get_theme(self):
        """Obtiene el tema actual completo"""
        return self.current_theme.copy()

    def is_dark(self):
        """Retorna True si el tema actual es oscuro"""
        return self.current_theme['name'] == 'dark'

    def register_callback(self, callback):
        """Registra una función que se llamará cuando cambie el tema"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def unregister_callback(self, callback):
        """Desregistra una función callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def notify_callbacks(self):
        """Notifica a todos los callbacks registrados"""
        for callback in self.callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error en callback: {e}")

    def get_matplotlib_style(self):
        """Retorna un diccionario con estilos para matplotlib"""
        if self.is_dark():
            return {
                'figure.facecolor': self.get_color('chart_bg'),
                'axes.facecolor': self.get_color('chart_bg'),
                'axes.edgecolor': self.get_color('border'),
                'axes.labelcolor': self.get_color('text'),
                'text.color': self.get_color('text'),
                'xtick.color': self.get_color('text'),
                'ytick.color': self.get_color('text'),
                'grid.color': self.get_color('border'),
                'legend.facecolor': self.get_color('panel'),
                'legend.edgecolor': self.get_color('border'),
            }
        else:
            return {
                'figure.facecolor': self.get_color('chart_bg'),
                'axes.facecolor': self.get_color('chart_bg'),
                'axes.edgecolor': self.get_color('border'),
                'axes.labelcolor': self.get_color('text'),
                'text.color': self.get_color('text'),
                'xtick.color': self.get_color('text'),
                'ytick.color': self.get_color('text'),
                'grid.color': self.get_color('border'),
                'legend.facecolor': 'white',
                'legend.edgecolor': self.get_color('border'),
            }

    def configure_matplotlib(self):
        """Configura matplotlib con el tema actual"""
        import matplotlib.pyplot as plt
        style = self.get_matplotlib_style()
        for key, value in style.items():
            plt.rcParams[key] = value

    def get_chart_colors(self):
        """Retorna una lista de colores para gráficas"""
        if self.is_dark():
            return [
                '#0A84FF', '#30D158', '#FFD60A', '#FF453A', '#5E5CE6',
                '#FF9F0A', '#FF375F', '#5AC8FA', '#AF52DE', '#64D2FF'
            ]
        else:
            return [
                '#0A84FF', '#30D158', '#FFD60A', '#FF3B30', '#5E5CE6',
                '#FF9F0A', '#FF375F', '#5AC8FA', '#AF52DE', '#64D2FF'
            ]


# Instancia global del gestor de temas
theme_manager = ThemeManager()
