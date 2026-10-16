# Documento de Especificación Técnica: Juego Shooter 2D (Escenario B - Arquitectura Limpia)

> \*\*Instrucciones para OpenCode:\*\* Actúa como un Arquitecto de Software y Desarrollador Senior de Python. Tu tarea es generar la implementación completa de un juego de disparos 2D en `pygame` (o `pygame-ce`) siguiendo estrictamente la especificación de arquitectura y reglas de negocio descritas a continuación.

\---

## 1\. Objetivo del Proyecto

Construir una aplicación de juego 2D en Python utilizando únicamente figuras geométricas primitivas (rectángulos y círculos) en modo *Standalone*, implementando una **Arquitectura Desacoplada (Model-View-Controller / Arquitectura Limpia)**.

El código debe estar estructurado de tal manera que la lógica del juego pueda migrarse a un servidor autoritativo de red en el futuro sin modificar la capa del modelo ni la capa de renderizado.

\---

## 2\. Reglas de Negocio (Business Rules)

1. **RN-01 (Cadencia de Disparo):** Cada jugador tiene una cadencia máxima de disparo. No se puede emitir un proyectil si han transcurrido menos de 200 ms desde el disparo anterior.
2. **RN-02 (Asignación de Puntos):** Cada impacto de proyectil contra un enemigo destruye ambas entidades y otorga +10 puntos al puntaje global.
3. **RN-03 (Límites Espaciales):** La posición horizontal x de la nave debe restringirse estrictamente dentro del rango {ANCHO} -{ancho\_nave}.
4. **RN-04 (Recolector de Basura / Purga):** Toda entidad de proyectil con y < 0 y enemigo con y > ALTO debe eliminarse del estado para prevenir fugas de memoria.
5. **RN-05 (Soberanía del Estado):** Toda modificación de vida, puntaje, creación o eliminación de entidades reside únicamente dentro del modelo `GameState`. La vista es de solo lectura.

\---

## 3\. Especificación de Arquitectura y Componentes

El código debe estar estrictamente dividido en las siguientes capas dentro del script:

### Capa 1: Dominio y Comandos

* Define un `Enum` llamado `Command` con las acciones abstractas: `MOVE\_LEFT`, `MOVE\_RIGHT`, `SHOOT`.

### Capa 2: Modelo del Dominio (Puro Python)

* **`Player`**: Representa la nave. Mantiene coordenadas $(x, y)$, dimensiones, velocidad, tiempo del último disparo y tiempo de recarga 20ms.
* **`Bullet`**: Representa el proyectil vertical. Contiene coordenadas (x, y), dimensiones y velocidad.
* **`Enemy`**: Representa un obstáculo circular. Contiene coordenadas (x, y), radio y velocidad.
* **RESTRICCIÓN CRÍTICA:** Ninguna de estas clases puede importar o instanciar objetos de `pygame` (como `pygame.Rect` o `pygame.Surface`). Las colisiones deben calcularse algebraicamente.

### Capa 3: Estado Central (`GameState`)

* Mantiene el diccionario de jugadores, lista de proyectiles, lista de enemigos, puntaje total y dimensiones del mapa 800x600.
* **`process\_command(player\_id, command, current\_time)`**: Ejecuta las acciones indicadas por las abstracciones de comandos.
* **`update()`**: Avanza la simulación lógica en un tick, genera enemigos con un temporizador, resuelve colisiones y aplica las reglas de negocio.
* **`get\_snapshot()`**: Devuelve una representación en diccionario plano (Data Transfer Object / JSON-like) con tipos nativos (`int`, `float`, `list`, `dict`) conteniendo la foto del estado actual.

### Capa 4: Captura de Entradas (`LocalInputHandler`)

* Lee eventos de teclado mediante `pygame.key.get\_pressed()`.
* Mapea teclas locales a una lista de enum `Command` (ejemplo: `K\_LEFT` $\\rightarrow$ `Command.MOVE\_LEFT`).

### Capa 5: Renderizador (`PygameRenderer`)

* Recibe exclusivamente el diccionario generado por `get\_snapshot()`.
* Limpia la pantalla y dibuja:

  * Jugadores como **rectángulos verdes**.
  * Proyectiles como **rectángulos amarillos**.
  * Enemigos como **círculos rojos**.
  * Puntaje en la esquina superior izquierda usando `pygame.font`.

### Capa 6: Orquestador / Bucle Principal (`main`)

* Configura la ventana a 800 x 600 px a 60 FPS.
* Coordina el flujo secuencial en cada frame:

  1. Capturar comandos (`InputHandler`).
  2. Procesar comandos en el modelo (`GameState`).
  3. Actualizar simulación física (`GameState.update()`).
  4. Extraer snapshot (`GameState.get\_snapshot()`).
  5. Dibujar escena (`PygameRenderer.render(snapshot)`).

\---

## 4\. Requisitos de Entrega para OpenCode

1. Entrega el código siguiendo principios SOLID y clean code.
2. Asegúrate de que el archivo funcione tanto con `pygame` tradicional como con `pygame-ce`.
3. Incluye comentarios breves identificando cada capa arquitectónica para su presentación y análisis.

\---

## 5\. Implementación Entregada (Monojugador local)

El proyecto está completo y modularizado en 7 archivos, cada uno mapeado a una capa de la arquitectura limpia:

| Archivo | Capa | Contenido |
|---------|------|-----------|
| `compat.py` | Utilidad | Compatibilidad `pygame` / `pygame-ce` (try/except de import) |
| `commands.py` | Capa 1: Dominio y Comandos | `Enum Command` con `MOVE_LEFT`, `MOVE_RIGHT`, `SHOOT` |
| `domain.py` | Capa 2: Modelo del Dominio | `Player`, `Bullet`, `Enemy` — Puro Python, sin `pygame` |
| `state.py` | Capa 3: Estado Central | `GameState` con `process_command`, `update`, `get_snapshot` |
| `input_handler.py` | Capa 4: Captura de Entradas | `LocalInputHandler` que mapea teclas a `Command` |
| `renderer.py` | Capa 5: Renderizador | `PygameRenderer` que dibuja exclusivamente desde `get_snapshot()` |
| `main.py` | Capa 6: Orquestador | Ventana 800×600 a 60 FPS y bucle secuencial de 5 etapas |

### Reglas de negocio implementadas (RN-01 a RN-05)

* **RN-01:** Cadencia máxima de disparo de 200 ms respetada en `GameState._shoot`.
* **RN-02:** Impacto bala-enemigo destruye ambas entidades y suma +10 puntos.
* **RN-03:** Posición horizontal `x` de la nave restringida a `[0, ANCHO - ancho_nave]`.
* **RN-04:** Purga de proyectiles con `y < 0` y enemigos con `y > ALTO`.
* **RN-05:** Toda modificación de estado reside en `GameState`; la vista es de solo lectura.

### Cómo ejecutar (monojugador local)

```bash
python main.py
```

Controles: flechas izquierda/derecha (o A/D) para moverse, espacio para disparar.

\---

## 6\. Modo Multijugador Online (Red Local)

El juego soporta modo **cliente-servidor autoritativo** para 2 jugadores en red local. El servidor ejecuta la lógica del juego (`GameState`) y es la única fuente de verdad; los clientes solo envían inputs y renderizan snapshots recibidos.

### Archivos de red

| Archivo | Rol |
|---------|-----|
| `common.py` | Constantes de red, protocolo JSON y funciones de serialización |
| `server.py` | Servidor autoritativo (puerto 5555, acepta 2 clientes: p1 y p2) |
| `client.py` | Cliente que se conecta, envía inputs y renderiza el snapshot |
| `main.py` | Punto de entrada: `python main.py server` o `python main.py client [host]` |

### Arquitectura de red

1. El servidor escucha en `0.0.0.0:5555` y acepta exactamente 2 clientes.
2. Cada cliente recibe su identificador (`p1` o `p2`) tras conectar.
3. Los clientes envían sus inputs (como lista de `Command`) al servidor cada frame.
4. El servidor procesa los inputs, actualiza `GameState` a 60 FPS y transmite el `snapshot` a ambos clientes.
5. Cada cliente renderiza únicamente desde el snapshot recibido (vista de solo lectura).

### Posiciones y controles por jugador

| Jugador | Posición inicial | Teclas movimiento | Tecla disparo |
|---------|-----------------|-------------------|---------------|
| `p1` | Borde inferior izquierda (x=150) | Flechas Izq/Der o A/D | Espacio |
| `p2` | Borde inferior derecha (x=610) | A/D o Flechas Izq/Der | Shift Izquierdo |

Cada jugador tiene su **puntaje individual**, mostrado en su respectiva esquina (P1 verde a la izquierda, P2 cian a la derecha). La bala conoce a su dueño (`player_id`), por lo que el puntaje se asigna correctamente al jugador que disparó.

### Cómo ejecutar (multijugador)

Terminal 1 (servidor):
```bash
python main.py server
```

Terminal 2 (cliente 1, misma máquina):
```bash
python main.py client 127.0.0.1
```

Terminal 3 (cliente 2, otra máquina de la red):
```bash
python main.py client <IP_del_servidor>
```

### Estado del repositorio

* Rama: `main`
* Commit final: `82fca0f` — `docs: actualizar context.md con sección de implementación entregada`
* Repositorio remoto: `https://github.com/gfCertus/shooter2.git` (usuario `gfcertus`)

