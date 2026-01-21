# Noticias IA - News Aggregator

Aplicación de noticias construida con Streamlit y SQLite, diseñada para desplegarse en Railway.
Muestra noticias de Cancillería, Perú y Mundo con análisis de sentimiento básico.

## Instalación Local

1.  Crear entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

2.  Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3.  Ejecutar la aplicación:
    ```bash
    streamlit run app.py
    ```

## Despliegue en Railway

1.  Subir este repositorio a GitHub.
2.  Conectar Railway al repositorio.
3.  Railway detectará automáticamente el `Procfile` y `requirements.txt`.
4.  ¡Listo!

## Estructura

- `app.py`: Interfaz principal y lógica de visualización.
- `rss_fetcher.py`: Lógica para obtener RSS y analizar sentimiento.
- `database.py`: Manejo de base de datos SQLite.
- `requirements.txt`: Librerías necesarias.
