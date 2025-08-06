

```grit
language python
// Matches typical lambda_handler headers with or without types and with or without return
`$header
    $doc
    $rest` where {
  // $header: one of these forms of the lambda_handler signature
  $header <: or {
    `def lambda_handler(event, context):`,
    `def lambda_handler(event: $t1, context: $t2):`,
    `def lambda_handler(event: $t1, context: $t2) -> $ret:`
  },
  // The first statement of the block is the docstring
  $doc <: string(),
  // Avoid adding if there is already a direct log/print of the event
  $rest <: not contains or {
    `logger.$method(event, $...)`,
    `print(event, $...)`
  }
} => `$header
    $doc
    logger.info('Event received:', extra=event)
    $rest`
```
