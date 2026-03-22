# SaludAI - Seguimiento de Salud con GraphRAG

Aplicación de seguimiento de síntomas de salud con chat interactivo, detección de patrones y visualización de tendencias.

## Características

- 💬 **Chat interactivo** para describir síntomas
- 🧠 **GraphRAG** construido con Zep para relacionar síntomas-tratamientos
- 📊 **Detección de patrones** recurrentes
- 🚨 **Sistema de alertas** para síntomas críticos
- 📈 **Visualización** de tendencias y puntuaciones de salud

## Requisitos

- Python 3.11+
- API Key de Zep (obtener en [getzep.com](https://getzep.com))

## Instalación

```bash
cd salud
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu ZEP_API_KEY
```

## Ejecución local

```bash
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Subir el código a GitHub
2. Ir a [share.streamlit.io](https://share.streamlit.io)
3. Conectar repositorio
4. Configurar secrets con `ZEP_API_KEY`

## Estructura del Proyecto

```
salud/
├── app.py              # Aplicación principal Streamlit
├── requirements.txt   # Dependencias
├── .streamlit/
│   └── config.toml    # Configuración de tema
├── utils/
│   ├── __init__.py
│   ├── zep_client.py  # Cliente de Zep GraphRAG
│   ├── patterns.py    # Detector de patrones
│   └── alerts.py      # Sistema de alertas
└── .env.example       # Template de variables de entorno
```

## API Keys Requeridas

| Servicio | Propósito | URL |
|----------|-----------|-----|
| Zep | GraphRAG y memoria de síntomas | getzep.com |
