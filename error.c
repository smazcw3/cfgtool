
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>

#include "error.h"

/* Reports a fatal error and exits the application */
void fatal (const char *fmt, ...)
{
  va_list ap;
  va_start (ap, fmt);
  fprintf (stderr, "fatal: ");
  vfprintf (stderr, fmt, ap);
  fprintf (stderr, "\n");
  va_end (ap);
  exit (1);
}
