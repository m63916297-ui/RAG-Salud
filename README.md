# 🏥 SaludAI - Sistema de Seguimiento de Salud con GraphRAG

Aplicación web de seguimiento de síntomas de salud con chat interactivo, detección de patrones recurrentes y visualización de tendencias utilizando Zep como motor de GraphRAG.

Streamlit Frontend
https://rag-salud-ah87rrhjpejswxr4aezkz9.streamlit.app/

## 🚀 Características

- **💬 Chat Interactivo**: Registro de síntomas mediante descripción natural
- **👤 Perfil del Paciente**: Nombre, edad, correo, exámenes y tratamientos
- **🧠 GraphRAG con Zep**: Construcción automática de grafos de conocimiento síntomas-tratamientos
- **📊 Detección de Patrones**: Identificación de síntomas recurrentes y tendencias
- **🚨 Sistema de Alertas**: Detección de síntomas críticos con recomendaciones
- **📈 Visualización**: Gráficos de tendencias, distribución y línea de tiempo de tratamientos
- **💾 Exportación**: Descarga de registros en formato JSON

## 📁 Estructura del Proyecto

```
salud/
├── app.py                      # Aplicación principal Streamlit
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Este archivo
├── .env                        # Variables de entorno (API keys)
├── .env.example                # Template de variables de entorno
├── .streamlit/
│   └── config.toml            # Configuración de tema y servidor
└── utils/
    ├── __init__.py            # Módulo de utilidades
    ├── zep_client.py          # Cliente de Zep GraphRAG
    ├── patterns.py            # Detector de patrones recurrentes
    └── alerts.py             # Sistema de alertas y puntuación de salud
```

## 📋 Archivos Detallados

### app.py
Aplicación principal que integra todos los componentes:

**Funcionalidades:**
- Interfaz de usuario con Streamlit
- Formulario de registro de síntomas con campos扩展idos
- Visualización de tendencias con Plotly
- Integración con Zep API para GraphRAG
- Exportación de datos

**Campos del formulario:**
- Nombre completo
- Edad
- Correo electrónico
- Exámenes realizados
- Tratamiento actual
- Descripción de síntomas

### utils/zep_client.py
Cliente para integración con Zep API:

**Clases:**
- `ZepHealthClient`: Clase principal para conexión con Zep

**Métodos:**
- `add_symptom_entry()`: Registra síntomas en el grafo de conocimiento
- `get_symptom_context()`: Obtiene contexto de síntomas previos
- `get_knowledge_graph()`: Recupera el grafo de conocimiento
- `query_treatments()`: Busca tratamientos relacionados
- `build_symptom_graph()`: Construye estructura de nodos y aristas

### utils/patterns.py
Detector de patrones recurrentes en síntomas:

**Categorías de síntomas detectadas:**
- Dolor de cabeza (cefalea, migraña, jaqueca)
- Fatiga (cansancio, agotamiento)
- Dolor muscular (mialgia)
- Insomnio (dificultad para dormir)
- Ansiedad (estrés, nervios)
- Dolor de estómago (náusea, indigestión)
- Mareo (vértigo)
- Problemas respiratorios (tos, congestión)

**Funcionalidades:**
- Extracción de síntomas del texto
- Análisis de severidad (alta, media, baja)
- Detección de duración temporal
- Identificación de patrones horarios
- Recomendaciones personalizadas

### utils/alerts.py
Sistema de alertas y puntuación de salud:

**Síntomas críticos detectados:**
- Dolor en el pecho
- Dificultad para respirar
- Sangrado
- Fiebre alta
- Desmayo

**Funcionalidades:**
- Verificación de síntomas críticos
- Análisis de tendencias de severidad
- Generación de puntuación de salud (0-100)
- Interpretación de patrones

### .streamlit/config.toml
Configuración visual de la aplicación:
- Tema oscuro personalizado
- Color primario: #00C896
- Configuración del servidor

## 🔑 API Keys Requeridas

| Servicio | Propósito | URL |
|----------|-----------|-----|
| **Zep** | GraphRAG y memoria de síntomas | [getzep.com](https://getzep.com) |

## ⚙️ Instalación

### 1. Clonar o descargar el proyecto

```bash
cd salud
```

### 2. Crear entorno virtual (opcional pero recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` y agregar tu API key de Zep:
```
ZEP_API_KEY=tu_api_key_de_zep
```

## 🚀 Ejecución

### Ejecución local

```bash
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

### Despliegue en Streamlit Cloud

1. **Subir a GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/tu-usuario/saludai.git
   git push -u origin main
   ```

2. **Configurar en Streamlit Cloud**
   - Ir a [share.streamlit.io](https://share.streamlit.io)
   - Conectar repositorio de GitHub
   - Seleccionar rama y archivo principal (`app.py`)

3. **Agregar Secrets**
   En Streamlit Cloud, ir a Settings > Secrets y agregar:
   ```
   ZEP_API_KEY = "tu_api_key_de_zep"
   ```

## 📊 Uso de la Aplicación

### 1. Registro de Paciente
- Ingresar nombre, edad y correo en el panel lateral
- Estos datos se asociarán a todos los registros

### 2. Registro de Síntomas
- Completar el formulario con:
  - **Exámenes realizados**: Análisis, radiografías, etc.
  - **Tratamiento actual**: Medicamentos, dosis, etc.
  - **Descripción de síntomas**: Narrativa libre del problema
- Clic en "Registrar" para guardar

### 3. Visualización
- **Tendencias**: Gráfico de evolución de síntomas
- **Distribución**: Porcentaje por categoría
- **Línea de tiempo**: Tratamientos aplicados

### 4. GraphRAG
- El sistema construye automáticamente un grafo de conocimiento
- Conecta síntomas con tratamientos
- Detecta patrones recurrentes

### 5. Alertas
- Síntomas críticos generan alertas inmediatas
- Se sugieren acciones y recomendaciones

## 🛠️ Tecnologías

- **Frontend**: Streamlit 1.28+
- **Visualización**: Plotly 5.18+
- **GraphRAG**: Zep Cloud SDK
- **Gestión de datos**: Pandas
- **Variables de entorno**: python-dotenv

## 📝 Licencia

Este proyecto es con fines educativos y de demostración.

## 🤝 Contribuir

1. Fork el repositorio
2. Crear una rama (`git checkout -b feature/nueva-funcion`)
3. Commit los cambios (`git commit -m 'Agregar nueva función'`)
4. Push a la rama (`git push origin feature/nueva-funcion`)
5. Abrir un Pull Request

## 📞 Soporte

Para reportar bugs o solicitar características, abrir un issue en el repositorio.

---

**Nota de Seguridad**: No almacene API keys directamente en el código. Use variables de entorno o secrets de Streamlit Cloud.
