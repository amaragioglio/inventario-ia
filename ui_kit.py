"""
Sistema visual de la aplicación: un solo lugar para botones y texto.

Principios (aplicados con la guía de diseño Impeccable, modo "Operate"):
- Es una herramienta de trabajo: claridad y constancia antes que adorno.
- Un solo color de acento, reservado para la acción principal y la selección.
- Rojo solo para acciones destructivas o estados críticos.
- Sin emojis como íconos; el texto del botón nombra la acción.
- Contraste de texto mínimo 4.5:1 en ambos temas.

`instalar()` reemplaza tk.Button por `Boton` antes de crear la interfaz, así
todos los botones de la app (incluidas ventanas secundarias) siguen el mismo
sistema sin tener que reescribir cada llamada.
"""

import re
import tkinter as tk

_ButtonOriginal = tk.Button

# Rol según la acción que nombra el botón.
_PRIMARIAS = ("nuevo", "nueva", "guardar", "crear", "agregar", "registrar", "confirmar")
_PELIGRO = ("eliminar", "borrar", "cancelar pedido")

# Quita emojis, símbolos y flechas usados como "íconos" al inicio o final del texto.
_ADORNO = re.compile(
    r"^[\s←-⯿✀-➿\U0001F000-\U0001FAFF️‍+✓✕✔✖•·]+|"
    r"[\s←-⯿\U0001F000-\U0001FAFF️]+$")


def limpiar_texto(texto):
    """'💾 Guardar' -> 'Guardar'. Mantiene el texto si queda vacío."""
    if not isinstance(texto, str):
        return texto
    limpio = _ADORNO.sub("", texto).strip()
    return limpio or texto.strip()


def rol_por_texto(texto):
    t = (texto or "").lower()
    if any(p in t for p in _PELIGRO):
        return "peligro"
    if any(t.startswith(p) for p in _PRIMARIAS):
        return "principal"
    return "secundario"


class Paleta:
    """Se rellena desde ThemeManager con el tema activo."""
    colores = {}

    @classmethod
    def c(cls, clave, defecto="#000000"):
        return cls.colores.get(clave, defecto)


def _estilo(rol):
    c = Paleta.c
    if rol == "principal":
        return dict(bg=c("primary"), fg=c("on_primary"), hover=c("primary_hover"), borde=c("primary"))
    if rol == "peligro":
        return dict(bg=c("panel"), fg=c("danger"), hover=c("danger_soft"), borde=c("border_strong"))
    if rol == "alerta":
        return dict(bg=c("danger_soft"), fg=c("danger"), hover=c("danger_soft_hover"), borde=c("danger_soft"))
    return dict(bg=c("panel"), fg=c("text"), hover=c("hover"), borde=c("border_strong"))


class Boton(_ButtonOriginal):
    """Botón con roles. Ignora colores sueltos que le pase el código viejo."""

    _CLAVES_COLOR = {"bg", "background", "fg", "foreground",
                     "activebackground", "activeforeground"}

    def __init__(self, master=None, cnf=None, rol=None, **kw):
        kw = {**(cnf or {}), **kw}
        for clave in self._CLAVES_COLOR:
            kw.pop(clave, None)
        texto = limpiar_texto(kw.get("text", ""))
        if "text" in kw:
            kw["text"] = texto
        compacto = kw.pop("compacto", False)
        kw.setdefault("font", ("Segoe UI Semibold", 10))
        kw.update(relief=tk.FLAT, borderwidth=0, cursor="hand2",
                  padx=12 if compacto else 18, pady=5 if compacto else 8,
                  highlightthickness=1, takefocus=True)
        super().__init__(master, **kw)
        self._rol = rol or rol_por_texto(texto)
        self._pintar()
        self.bind("<Enter>", lambda e: self._hover(True), add="+")
        self.bind("<Leave>", lambda e: self._hover(False), add="+")
        self.bind("<FocusIn>", lambda e: self._foco(True), add="+")
        self.bind("<FocusOut>", lambda e: self._foco(False), add="+")
        self.bind("<Return>", lambda e: self.invoke(), add="+")

    # --- API ---
    def set_rol(self, rol):
        self._rol = rol
        self._pintar()

    # --- interno ---
    def _pintar(self):
        e = _estilo(self._rol)
        super().configure(bg=e["bg"], fg=e["fg"], activebackground=e["hover"],
                          activeforeground=e["fg"], highlightbackground=e["borde"],
                          highlightcolor=Paleta.c("focus"),
                          disabledforeground=Paleta.c("text_disabled"))

    def _hover(self, dentro):
        if str(self["state"]) == "disabled":
            return
        e = _estilo(self._rol)
        super().configure(bg=e["hover"] if dentro else e["bg"])

    def _foco(self, con_foco):
        super().configure(highlightthickness=2 if con_foco else 1)

    def configure(self, cnf=None, **kw):
        kw = {**(cnf or {}), **kw}
        for clave in self._CLAVES_COLOR:
            kw.pop(clave, None)  # el color lo decide el rol
        if "text" in kw:
            kw["text"] = limpiar_texto(kw["text"])
        return super().configure(**kw) if kw else super().configure()

    config = configure

    def __setitem__(self, clave, valor):
        if clave in self._CLAVES_COLOR:
            return
        if clave == "text":
            valor = limpiar_texto(valor)
        super().__setitem__(clave, valor)


def instalar(theme_manager):
    """Activa el sistema visual. Llamar antes de construir la interfaz."""
    Paleta.colores = dict(theme_manager.current_theme)
    tk.Button = Boton


def actualizar(theme_manager):
    Paleta.colores = dict(theme_manager.current_theme)
