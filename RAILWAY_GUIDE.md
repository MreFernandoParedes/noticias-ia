# Guía de Despliegue en Railway

## 1. Configurar Variables de Entorno

Para que la IA funcione en producción, necesitas agregar tu API Key en Railway:

1.  Entra al dashboard de tu proyecto en **Railway**.
2.  Ve a la pestaña **Variables**.
3.  Haz clic en **New Variable**.
4.  En **VARIABLE_NAME** escribe: `OPENAI_API_KEY`
5.  En **VALUE** pega tu clave: `sk-...`
6.  Haz clic en **Add**.

Railway redeployará automáticamente tu aplicación con la nueva configuración.

## 2. Archivos Importantes

Asegúrate de que estos archivos estén en tu repositorio (ya creados):

-   `Procfile`: Instrucciones de arranque (`web: streamlit run...`).
-   `runtime.txt`: Versión de Python (`python-3.11`).
-   `requirements.txt`: Dependencias (`openai`, `streamlit`, `python-dotenv`, etc).
