# 📊 Actualizador de Organigramas en PDF

Sistema automatizado para modificar organigramas en PDF sin alterar el diseño visual.

## ⚡ Nuevo: Sistema Inteligente con Detección de Superposiciones

### 🧠 Actualizador Inteligente (Recomendado)
Verifica automáticamente que no se cubran cargos ni líneas:

```bash
# 1. Extraer posiciones organizacionales
python extract_positions.py

# 2. Actualizar con verificación automática de superposiciones
python update_smart.py "02_ORGANIGRAMA_LUCAS" "Lucas Capuano" "Diego Piñero"
```

**Ventajas:**
- ✅ Detecta elementos cercanos (cargos, títulos)
- ✅ Ajusta automáticamente el área de reemplazo
- ✅ Padding adaptativo según proximidad
- ✅ Clasifica elementos: CARGO, NOMBRE, OTROS

### 📊 Base de Datos de Coordenadas (Alternativa)
```bash
python extract_coordinates.py
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas" "Diego Piñero"
```

**📖 [Ver documentación completa del sistema de BD](DATABASE.md)**

## 🚀 Uso Rápido

### Comando Simple
```bash
python update_pdf.py "<ruta_al_pdf>" "<texto_a_buscar>" "<texto_de_reemplazo>"
```

### Ejemplo Real
```bash
python update_pdf.py "input/templates/02_ORGANIGRAMA_LUCAS.pdf" "Lucas Capuano" "Diego Piñero"
```

### Resultado
- Busca automáticamente "Lucas Capuano" en el PDF
- Extrae sus coordenadas exactas
- Genera un overlay con "Diego Piñero"
- Guarda el resultado en `output/02_ORGANIGRAMA_LUCAS_actualizado.pdf`

## 📁 Estructura del Proyecto

```
orgchart-andreani-pdf/
├── update_pdf.py          # ⭐ Script principal (todo en uno)
├── main.py                # Pipeline por lotes (procesa múltiples PDFs)
├── src/                   # Módulos del sistema
│   ├── models.py          # Modelos de datos
│   ├── renderer.py        # Motor de texto (ReportLab)
│   ├── merger.py          # Fusionador de PDFs (Pikepdf)
│   ├── datalake.py        # Fuente de datos
│   └── pipeline.py        # Orquestador
├── input/templates/       # PDFs base + configs JSON
└── output/                # PDFs generados
```

## 🔧 Instalación

```bash
pip install -r requirements.txt
```

## 📝 Dos Modos de Uso

### 1️⃣ Modo Simple (Recomendado)
Para modificar un PDF específico:
```bash
python update_pdf.py "mi_organigrama.pdf" "Nombre Viejo" "Nombre Nuevo"
```

### 2️⃣ Modo Pipeline
Para procesar múltiples organigramas configurados:
```bash
python main.py
```

## 🎯 Casos de Uso

### Cambiar un nombre en un organigrama
```bash
python update_pdf.py "Organigrama IT.pdf" "Juan Pérez" "Ana García"
```

### Actualizar un cargo
```bash
python update_pdf.py "Organigrama CEO.pdf" "Gerente General\nCarlos López" "CEO\nMarta Rodríguez"
```

## ⚙️ Cómo Funciona

1. **Búsqueda Automática**: Usa `pdfplumber` para encontrar el texto original
2. **Extracción de Coordenadas**: Calcula la posición exacta (x, y, ancho, alto)
3. **Generación de Overlay**: Crea un PDF transparente con el texto nuevo usando `ReportLab`
4. **Fusión**: Superpone el texto sobre el PDF original con `Pikepdf`
5. **Salida**: Guarda el PDF actualizado sin modificar el diseño

## 🔗 Integración con SharePoint (Próximo)

El sistema está diseñado para integrarse con SharePoint:
- Leer PDFs desde `/Organigramas`
- Guardar resultados en `/Organigramas/A revisar`

## 💡 Notas Importantes

- El diseño visual del PDF **no se modifica**
- El texto debe existir en el PDF para poder ser reemplazado
- Las fuentes y tamaños se mantienen similares al original
- El script busca solo en la **primera página** del PDF

## 🛠️ Desarrollo

Para agregar nuevos organigramas al pipeline por lotes:
1. Crear archivo JSON en `input/templates/nombre.json`
2. Agregar datos en `src/datalake.py`
3. Ejecutar `python main.py`

Para calibración manual:
```bash
python calibrate_template.py
```
