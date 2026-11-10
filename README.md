# Apps de Home Assistant de Joaquín

Repositorio de Apps (antes "add-ons") para Home Assistant OS.

## Finanzas del hogar

Registro de gastos compartidos entre dos personas: compras en cuotas, tarjeta de crédito compartida, gastos fijos y cierre mensual con división proporcional al sueldo. Incluye proyección de los meses siguientes.

- Se abre desde la barra lateral de Home Assistant, también en la app del celular y desde fuera de casa (Nabu Casa o tu propio dominio).
- Usa el login de Home Assistant: no queda expuesta en internet.
- Los datos se guardan en la App (`/data/finanzas.json`) y entran en los backups de Home Assistant.
- Este repositorio contiene solo el código. **No subas aquí tus respaldos**: tienen sueldos y gastos.

### Instalar

1. En Home Assistant: **Configuración → Apps → Tienda de Apps**.
2. Menú ⋮ (arriba a la derecha) → **Repositorios** → pega la URL de este repositorio → **Agregar**.
3. Busca **Finanzas del hogar** → **Instalar**.
4. Activa **Mostrar en la barra lateral** e **Iniciar**.
5. Ábrela y, en **Resumen**, importa el archivo de respaldo (`respaldo-finanzas-AAAA-MM-DD.json`).

Para que otra persona la use, créale un usuario en **Configuración → Personas** (no necesita ser administrador). La App aparece en la barra lateral de todos los usuarios.

### Actualizar

Cuando se publica una versión nueva (cambia `version` en `finanzas_hogar/config.yaml`), Home Assistant muestra la actualización en **Configuración → Apps**. Si no aparece, en la Tienda de Apps usa ⋮ → **Buscar actualizaciones**. Los datos se conservan al actualizar.

### Respaldo

En la pestaña **Historial**, al final, puedes **Descargar respaldo** (un `.json` con todo) o **Importar respaldo**. Al importar se reemplazan los datos actuales; la App guarda antes una copia en `/data/antes-de-importar-*.json`.
