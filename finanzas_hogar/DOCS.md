# Finanzas del hogar

Gastos compartidos, compras en cuotas y cierre mensual entre dos personas, con división proporcional al sueldo.

## Primer uso

1. Inicia la App y ábrela desde la barra lateral (**Finanzas**).
2. En **Resumen**, usa **Importar respaldo** con tu archivo `.json`, o empieza de cero registrando gastos en **Movimientos**.

## Cómo funciona el cierre del mes

- **Sueldos**: cada mes se ingresa el sueldo líquido de cada uno; de ahí sale el % que paga cada uno.
- **Gastos fijos**: arriendo, gastos comunes, luz, agua, internet (lo que no se paga con la tarjeta).
- **Tarjetas Scotia (Signature y Platinum)**: se ingresa lo facturado en cada una. Se descuentan las compras personales (se cobran completas a su dueño) y las duplicadas; el resto se divide por sueldo.
- **Cuotas y gastos**: lo registrado en Movimientos que no va en la tarjeta.
- **Ajustes manuales**: diferencias puntuales.

El resultado indica quién le transfiere a quién y cuánto. Se puede cerrar el mes y marcar la transferencia como hecha.

## Datos y respaldos

Los datos viven en `/data/finanzas.json` dentro de la App y se incluyen en los backups de Home Assistant. En **Historial** puedes descargar o importar un respaldo manual.

## Acceso

La App solo responde a través del ingress de Home Assistant, así que siempre pide el login de Home Assistant.
