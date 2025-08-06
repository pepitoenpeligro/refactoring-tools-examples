
```grit
language python
// Finds the last import (import ... | from ... import ...)
// and rewrites to insert below the Powertools import + logger = Logger()
or { `import $mods` as $imp, `from $pkg import $names` as $imp } => `
$imp

from aws_lambda_powertools import Logger

logger = Logger()` where {
  // There must be prints in the file
  $program <: contains `print($_)`,                       // $program: complete program
  // Avoid duplicates
  $program <: not contains `from aws_lambda_powertools import Logger`,
  $program <: not contains `logger = Logger($...)`,
  // Ensure THIS is the last import: what comes after is NOT another import
  $next = after $imp,
  $next <: not or { `import $_`, `from $_ import $_` }
}
```
