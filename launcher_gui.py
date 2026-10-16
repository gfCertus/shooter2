"""
Launcher con interfaz gráfica (tkinter) para el Shooter 2D multijugador.

Permite configurar y lanzar:
  * Servidor: puerto de escucha.
  * Cliente: IP y puerto del servidor.

Los ejecutables del servidor y cliente deben estar en la carpela dist/.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")
SERVER_EXE = os.path.join(DIST_DIR, "shooter_server.exe")
CLIENT_EXE = os.path.join(DIST_DIR, "shooter_client.exe")

DEFAULT_PORT = 5555
DEFAULT_HOST = "127.0.0.1"


class ShooterLauncher(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Shooter 2D - Launcher Multijugador")
        self.geometry("420x320")
        self.resizable(False, False)

        self.server_proc: subprocess.Popen | None = None
        self.client_proc: subprocess.Popen | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Pestaña Servidor ---
        tab_server = ttk.Frame(notebook)
        notebook.add(tab_server, text="Servidor")

        ttk.Label(tab_server, text="Puerto de escucha:").pack(pady=(20, 5))
        self.var_server_port = tk.StringVar(value=str(DEFAULT_PORT))
        ent_port = ttk.Entry(tab_server, textvariable=self.var_server_port, width=10, justify="center")
        ent_port.pack(pady=5)

        self.btn_iniciar_server = ttk.Button(
            tab_server, text="Iniciar Servidor", command=self.toggle_server, width=25
        )
        self.btn_iniciar_server.pack(pady=20)

        self.lbl_server_status = ttk.Label(tab_server, text="Servidor detenido", foreground="gray")
        self.lbl_server_status.pack()

        # --- Pestaña Cliente ---
        tab_client = ttk.Frame(notebook)
        notebook.add(tab_client, text="Cliente")

        ttk.Label(tab_client, text="IP del servidor:").pack(pady=(20, 5))
        self.var_client_host = tk.StringVar(value=DEFAULT_HOST)
        ttk.Entry(tab_client, textvariable=self.var_client_host, width=20, justify="center").pack(pady=5)

        ttk.Label(tab_client, text="Puerto:").pack(pady=(10, 5))
        self.var_client_port = tk.StringVar(value=str(DEFAULT_PORT))
        ttk.Entry(tab_client, textvariable=self.var_client_port, width=10, justify="center").pack(pady=5)

        self.btn_conectar = ttk.Button(
            tab_client, text="Conectar Cliente", command=self.toggle_client, width=25
        )
        self.btn_conectar.pack(pady=20)

        self.lbl_client_status = ttk.Label(tab_client, text="Cliente detenido", foreground="gray")
        self.lbl_client_status.pack()

        # --- Footer ---
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=(0, 5))
        lbl_nota = ttk.Label(
            self,
            text="Asegúrate de que shooter_server.exe y shooter_client.exe estén en la carpeta dist/",
            foreground="gray",
        )
        lbl_nota.pack(pady=(0, 10))

    # ------------------------------------------------------------------
    # Servidor
    # ------------------------------------------------------------------
    def toggle_server(self) -> None:
        if self.server_proc is None:
            self._start_server()
        else:
            self._stop_server()

    def _start_server(self) -> None:
        port_text = self.var_server_port.get().strip()
        if not port_text.isdigit():
            messagebox.showerror("Error", "El puerto debe ser un número válido.")
            return
        port = int(port_text)
        if not (1 <= port <= 65535):
            messagebox.showerror("Error", "El puerto debe estar entre 1 y 65535.")
            return

        if not os.path.isfile(SERVER_EXE):
            messagebox.showerror(
                "Error",
                f"No se encontró {SERVER_EXE}\n\nCompila primero con PyInstaller.",
            )
            return

        try:
            self.server_proc = subprocess.Popen(
                [SERVER_EXE, "--port", str(port)],
                cwd=BASE_DIR,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
            self.btn_iniciar_server.config(text="Detener Servidor")
            self.lbl_server_status.config(text=f"Servidor en puerto {port}", foreground="green")
            self.var_server_port.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el servidor:\n{e}")

    def _stop_server(self) -> None:
        if self.server_proc and self.server_proc.poll() is None:
            try:
                self.server_proc.terminate()
                self.server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_proc.kill()
        self.server_proc = None
        self.btn_iniciar_server.config(text="Iniciar Servidor")
        self.lbl_server_status.config(text="Servidor detenido", foreground="gray")
        self.var_server_port.config(state="normal")

    # ------------------------------------------------------------------
    # Cliente
    # ------------------------------------------------------------------
    def toggle_client(self) -> None:
        if self.client_proc is None:
            self._start_client()
        else:
            self._stop_client()

    def _start_client(self) -> None:
        host = self.var_client_host.get().strip()
        port_text = self.var_client_port.get().strip()
        if not port_text.isdigit():
            messagebox.showerror("Error", "El puerto debe ser un número válido.")
            return
        port = int(port_text)
        if not (1 <= port <= 65535):
            messagebox.showerror("Error", "El puerto debe estar entre 1 y 65535.")
            return

        if not os.path.isfile(CLIENT_EXE):
            messagebox.showerror(
                "Error",
                f"No se encontró {CLIENT_EXE}\n\nCompila primero con PyInstaller.",
            )
            return

        try:
            self.client_proc = subprocess.Popen(
                [CLIENT_EXE, "--host", host, "--port", str(port)],
                cwd=BASE_DIR,
            )
            self.btn_conectar.config(text="Desconectar Cliente")
            self.lbl_client_status.config(text=f"Conectado a {host}:{port}", foreground="green")
            self.var_client_host.config(state="disabled")
            self.var_client_port.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el cliente:\n{e}")

    def _stop_client(self) -> None:
        if self.client_proc and self.client_proc.poll() is None:
            try:
                self.client_proc.terminate()
                self.client_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.client_proc.kill()
        self.client_proc = None
        self.btn_conectar.config(text="Conectar Cliente")
        self.lbl_client_status.config(text="Cliente detenido", foreground="gray")
        self.var_client_host.config(state="normal")
        self.var_client_port.config(state="normal")

    # ------------------------------------------------------------------
    def on_closing(self) -> None:
        self._stop_server()
        self._stop_client()
        self.destroy()


def main() -> None:
    app = ShooterLauncher()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()
