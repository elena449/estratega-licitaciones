# Estratega de Licitaciones · Chakakuna

App de análisis de TdR con matching de proyectos históricos usando Gemini API.

## Cómo usar

### 1. Obtener API Key de Gemini
- Ve a https://aistudio.google.com/apikey
- Crea una API Key gratuita

### 2. Instalar y correr localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 3. Deploy en Streamlit Cloud (recomendado para el equipo)
1. Sube esta carpeta a un repositorio GitHub (puede ser privado)
2. Ve a https://share.streamlit.io
3. Conecta tu cuenta GitHub
4. Selecciona el repositorio y el archivo `app.py`
5. Deploy → la app queda disponible en una URL pública para todo el equipo

**Recomendación**: Guarda la API Key como "Secret" en Streamlit Cloud para no tener que ingresarla cada vez.

## Flujo de uso

1. **Configurar API Key** en el panel lateral
2. **Subir PDFs de proyectos** en el panel lateral (base de datos permanente de la sesión)
3. **Subir TdR** en la pestaña principal
4. Hacer clic en **"Generar Informe de Viabilidad"**
5. Usar la pestaña **Chat** para preguntas de seguimiento

## Modelo

Usa `gemini-2.0-flash` (gratuito con límites generosos).
