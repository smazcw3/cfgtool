
#include <stdlib.h>
#include <string.h>

#include "alloc.h"
#include "error.h"


/* Safe version of malloc */
void *mem_alloc (size_t size)
{
  void *ptr = malloc (size);
  if (ptr == NULL) fatal ("memory exhausted");
  return ptr;
}

/* Safe version of realloc */
void *mem_realloc (void *ptr, size_t size)
{
  void *p = realloc (ptr, size);
  if (p == NULL) fatal ("memory exhausted for realloc");
  return p;
}

/* A proxy to free */
void mem_free (void *ptr)
{
  free (ptr);
}
