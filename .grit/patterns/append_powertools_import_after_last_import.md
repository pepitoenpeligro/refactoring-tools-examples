
```grit
language python
// Encuentra el último import (import ... | from ... import ...)
// y reescribe para insertar debajo el import de Powertools + logger = Logger()
or { `import $mods` as $imp, `from $pkg import $names` as $imp } => `
$imp

from aws_lambda_powertools import Logger

logger = Logger()` where {
  // Debe haber prints en el archivo
  $program <: contains `print($_)`,                       // $program: programa completo
  // Evita duplicados
  $program <: not contains `from aws_lambda_powertools import Logger`,
  $program <: not contains `logger = Logger($...)`,
  // Asegura que ESTE es el último import: lo que viene después NO es otro import
  $next = after $imp,
  $next <: not or { `import $_`, `from $_ import $_` }
}
```
