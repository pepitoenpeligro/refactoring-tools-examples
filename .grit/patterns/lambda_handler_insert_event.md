

```grit
language python
// Encaja cabeceras típicas de lambda_handler con o sin tipos y con o sin return
`$header
    $doc
    $rest` where {
  // $header: una de estas formas de la firma de lambda_handler
  $header <: or {
    `def lambda_handler(event, context):`,
    `def lambda_handler(event: $t1, context: $t2):`,
    `def lambda_handler(event: $t1, context: $t2) -> $ret:`
  },
  // El primer statement del bloque es el docstring
  $doc <: string(),
  // Evita añadir si ya hay un log/print directo del event
  $rest <: not contains or {
    `logger.$method(event, $...)`,
    `print(event, $...)`
  }
} => `$header
    $doc
    logger.info('Event received:', extra=event)
    $rest`
```
