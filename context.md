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

