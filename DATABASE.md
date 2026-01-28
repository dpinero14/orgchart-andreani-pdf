# 🗄️ Base de Datos de Coordenadas

Sistema mejorado para actualizar organigramas usando una base de datos de coordenadas pre-calculadas.

## 🎯 Ventajas del Nuevo Sistema

✅ **Más rápido**: No necesita buscar las coordenadas cada vez  
✅ **Más confiable**: Las coordenadas están guardadas y validadas  
✅ **Más flexible**: Permite buscar por texto parcial  
✅ **Más escalable**: Fácil agregar nuevos organigramas

## 📊 Flujo de Trabajo

### 1️⃣ Extraer Coordenadas (Una sola vez)
```bash
python extract_coordinates.py
```

Esto genera `coordinates_db.json` con todas las coordenadas de texto de todos los PDFs.

**Salida esperada:**
```
🗺️  EXTRACTOR DE COORDENADAS DE ORGANIGRAMAS
============================================================
🔍 Encontrados 2 PDFs para procesar

📄 Procesando: input\templates\01_ORGANIGRAMA_CEO.pdf
  ✓ Extraídos 45 elementos de texto

📄 Procesando: input\templates\02_ORGANIGRAMA_LUCAS.pdf
  ✓ Extraídos 98 elementos de texto

✅ Base de datos guardada en: coordinates_db.json
📊 Total organigramas: 2
📝 Total elementos de texto: 143
```

### 2️⃣ Actualizar PDFs (Rápido)
```bash
python update_from_db.py "<org_id>" "<texto_a_buscar>" "<texto_nuevo>"
```

**Ejemplo:**
```bash
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas" "Diego Piñero"
```

## 📁 Estructura de la Base de Datos

El archivo `coordinates_db.json` tiene esta estructura:

```json
{
  "version": "1.0",
  "description": "Base de datos de coordenadas de organigramas",
  "organigramas": {
    "02_ORGANIGRAMA_LUCAS": {
      "pdf_path": "input/templates/02_ORGANIGRAMA_LUCAS.pdf",
      "page_dimensions": {
        "width": 792.0,
        "height": 612.0
      },
      "text_elements": [
        {
          "text": "Lucas",
          "x": 7.12,
          "y": 290.4,
          "w": 30.5,
          "h": 12.0
        },
        {
          "text": "Capuano",
          "x": 40.0,
          "y": 290.4,
          "w": 45.2,
          "h": 12.0
        }
      ]
    }
  }
}
```

## 🔄 Comparación de Métodos

### Método Original (`update_pdf.py`)
```bash
python update_pdf.py "input/templates/02_ORGANIGRAMA_LUCAS.pdf" "Lucas Capuano" "Diego Piñero"
```

- ❌ Busca coordenadas cada vez (lento)
- ❌ Requiere ruta completa del PDF
- ✅ No requiere configuración previa

### Método con Base de Datos (`update_from_db.py`)
```bash
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas" "Diego Piñero"
```

- ✅ Usa coordenadas pre-calculadas (rápido)
- ✅ Solo necesita el ID del organigrama
- ✅ Búsqueda más flexible (texto parcial)
- ❌ Requiere ejecutar `extract_coordinates.py` primero

## 🛠️ Casos de Uso

### Actualizar múltiples organigramas
```bash
# Extraer coordenadas una vez
python extract_coordinates.py

# Actualizar varios organigramas rápidamente
python update_from_db.py "01_ORGANIGRAMA_CEO" "Juan" "Pedro"
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas" "Diego"
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Gerente" "Director"
```

### Agregar un nuevo organigrama
1. Colocar el PDF en `input/templates/`
2. Ejecutar `python extract_coordinates.py`
3. Listo para usar con `update_from_db.py`

### Ver organigramas disponibles
```bash
python extract_coordinates.py
```

Muestra todos los organigramas y sus textos disponibles.

## 📝 Scripts Disponibles

| Script | Propósito | Cuándo usar |
|--------|-----------|-------------|
| `extract_coordinates.py` | Extrae coordenadas de todos los PDFs | Una vez al inicio o cuando se agregan PDFs nuevos |
| `update_from_db.py` | Actualiza PDFs usando la BD | Para actualizaciones rápidas y repetidas |
| `update_pdf.py` | Actualiza PDFs sin BD (original) | Para casos únicos o PDFs externos |

## 🔍 Búsqueda Inteligente

El sistema busca coincidencias parciales, por lo que puedes usar:

```bash
# Buscar por nombre completo
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas Capuano" "Diego Piñero"

# Buscar por solo el nombre
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Lucas" "Diego"

# Buscar por cargo
python update_from_db.py "02_ORGANIGRAMA_LUCAS" "Gerente" "Director"
```

## 💡 Tips

1. **Regenerar la BD**: Si modificas los PDFs originales, ejecuta nuevamente `extract_coordinates.py`
2. **Ver contenido**: Abre `coordinates_db.json` para ver todos los textos disponibles
3. **Coincidencias múltiples**: Si hay varias coincidencias, el sistema usa la primera y te muestra las demás
4. **Validación**: La BD te muestra errores claros si el texto no existe

## 🚀 Próximos Pasos

- [ ] Interfaz web para visualizar la base de datos
- [ ] Búsqueda por coordenadas aproximadas
- [ ] Soporte para múltiples páginas
- [ ] Exportar/importar configuraciones de reemplazo
- [ ] API REST para integración con otros sistemas
