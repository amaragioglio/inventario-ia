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

    # Paleta "libreta de bodega": neutros cálidos y un solo acento verde.
    # Pensada para una PC en el mostrador, de día. Todo texto cumple 4.5:1.

    LIGHT = {
        'name': 'light',
        'bg': '#F4F3EF',
        'panel': '#FFFFFF',
        'subtle': '#F8F7F4',
        'text': '#1D1F1E',
        'text_secondary': '#5E625F',
        'text_disabled': '#A3A6A3',
        'border': '#E4E2DB',
        'border_strong': '#CFCCC3',
        'shadow': '#E4E2DB',
        'primary': '#1F6F54',
        'primary_hover': '#185A44',
        'primary_soft': '#E3EFEA',
        'on_primary': '#FFFFFF',
        'focus': '#1F6F54',
        'success': '#237A4B',
        'warning': '#B25E09',
        'warning_text': '#9A5208',
        'danger': '#B42318',
        'danger_soft': '#FBE9E7',
        'danger_soft_hover': '#F6D7D3',
        'info': '#2D5F8B',
        'chart_bg': '#FFFFFF',
        'hover': '#F1F0EB',
        'accent': '#1F6F54',
        'card_bg': '#FFFFFF',
        'input_bg': '#FFFFFF',
        'tree_header': '#F1F0EB',
        'tree_selected': '#DCEBE4',
        'tree_odd_row': '#FFFFFF',
        'tree_even_row': '#FAF9F6',
    }

    DARK = {
        'name': 'dark',
        'bg': '#151716',
        'panel': '#1D201F',
        'subtle': '#232726',
        'text': '#ECEDEA',
        'text_secondary': '#A3A8A5',
        'text_disabled': '#6B706D',
        'border': '#2C302E',
        'border_strong': '#3D4240',
        'shadow': '#0E0F0F',
        'primary': '#4FB38D',
        'primary_hover': '#64C29E',
        'primary_soft': '#1E3A30',
        'on_primary': '#0F1B16',
        'focus': '#64C29E',
        'success': '#5CC28B',
        'warning': '#E8A34A',
        'warning_text': '#E8A34A',
        'danger': '#F2776B',
        'danger_soft': '#3A2220',
        'danger_soft_hover': '#4A2B28',
        'info': '#7FB0E0',
        'chart_bg': '#1D201F',
        'hover': '#262A29',
        'accent': '#4FB38D',
        'card_bg': '#1D201F',
        'input_bg': '#232726',
        'tree_header': '#232726',
        'tree_selected': '#24453A',
        'tree_odd_row': '#1D201F',
        'tree_even_row': '#202322',
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
        """Colores para gráficas: el acento y variaciones, más neutros cálidos."""
        if self.is_dark():
            return ['#4FB38D', '#7FC7AA', '#2F7F62', '#B2DCCB', '#D3A867',
                    '#8E948F', '#B8BDB9', '#5E6561', '#E2C79A', '#3D4240']
        return ['#1F6F54', '#4F9A7E', '#86BFA8', '#B9DACB', '#B98A3E',
                '#8E8A7E', '#B8B4A8', '#5E625F', '#D9C29A', '#D8D5CC']


# Instancia global del gestor de temas
theme_manager = ThemeManager()
