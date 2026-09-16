# Cut Overrides V3

`sourceRanges` sigue siendo verdad del master para el Cutter actual.

Cuando un evento `locked_to_source` se arrastra o trima de verdad, V3 conserva:

```json
{
  "editorialOverride": {
    "originalStart": 0,
    "originalEnd": 12,
    "reason": "timeline_drag",
    "requiresReview": true
  }
}
```

y registra en la pieza:

```json
{
  "cutOverrides": [
    {
      "eventId": "AR1",
      "originalTimeline": {"start": 0, "end": 12},
      "editorialTimeline": {"start": 2, "end": 14},
      "status": "needs_review",
      "sourceTruthUnchanged": true
    }
  ]
}
```

V3.0 no obliga al Cutter actual a consumir este campo. Un Cutter posterior podrá aprobar/resolver el override contra sourceRanges y word timing antes de renderizar.
