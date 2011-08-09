
#ifndef __ALLOC_H
#define __ALLOC_H

#include <stddef.h>

/* Safe version of malloc */
void *mem_alloc (size_t size);
/* Safe version of realloc */
void *mem_realloc (void *ptr, size_t size);
/* A proxy to free */
void mem_free (void *ptr);

#endif /* __ALLOC_H */
