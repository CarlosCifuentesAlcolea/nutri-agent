# Nutri Agent

Aplicacion de consola para leer la dieta de un Excel y mostrar las equivalencias
diarias segun si el usuario ha entrenado o no.

## Ejecucion

Para ejecutar la aplicacion, activa primero el entorno virtual:

```powershell
.venv\Scripts\activate
```

Despues inicia el programa principal:

```powershell
python app/main.py
```

La aplicacion preguntara si has entrenado hoy y mostrara el objetivo del dia:

- Hidratos
- Proteina
- Grasa

Tambien permite:

- Consultar equivalencias de hidratos, proteinas y grasas disponibles en el Excel.
- Registrar comidas durante el dia escribiendo el alimento consumido.
- Interpretar cantidades como `220ml cafe con leche` y calcular equivalencias.
- Ver las equivalencias consumidas.
- Ver cuanto queda para completar el objetivo diario.
- Sugerir una comida segun el momento del dia y la distribucion por comidas del Excel.
- Adaptar sugerencias a preferencias como `quiero algo con pavo y patatas`.
- Reiniciar el registro del dia.
