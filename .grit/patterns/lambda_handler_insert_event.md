# Insertar logger.info al inicio de lambda_handler (Python)

```grit
language python

`def lambda_handler($params) -> $ret:
    $body` => `def lambda_handler($params) -> $ret:
    logger.info('Event received:', extra=event)
    $body`

```
