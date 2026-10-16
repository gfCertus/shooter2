"""
Capa de Red: Constantes y protocolo de comunicación cliente-servidor.
"""
import json

HOST_SERVER = "0.0.0.0"  # Servidor escucha en todas las interfaces
HOST_CLIENT_DEFAULT = "127.0.0.1"  # Cliente se conecta a localhost por defecto
PORT = 5555
BUFFER_SIZE = 4096

# Alias de compatibilidad
HOST = HOST_SERVER

# Tipos de mensaje del protocolo
MSG_JOIN = "join"
MSG_INPUT = "input"
MSG_SNAPSHOT = "snapshot"
MSG_ERROR = "error"
MSG_FULL = "full"


def encode(msg: dict) -> bytes:
    """Serializa un mensaje a bytes con delimitador de nueva línea."""
    return (json.dumps(msg) + "\n").encode("utf-8")


def decode_line(buffer: str):
    """Extrae un mensaje JSON completo del buffer si hay una línea completa."""
    if "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        line = line.strip()
        if line:
            return json.loads(line), buffer
    return None, buffer
