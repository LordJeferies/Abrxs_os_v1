# R5 → R6

Los proyectos legacy con XR00–XR09 no deben reescribirse destructivamente.

Regla:
- conservar `legacyXrFamily`;
- asignar una familia R6 sólo después de revisar su función visual;
- no hacer mapeo ciego uno-a-uno sólo por número.

R6 simplifica la producción nueva; R5 sigue siendo válido para piezas antiguas.
