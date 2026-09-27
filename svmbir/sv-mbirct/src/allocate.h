#ifndef _ALLOCATE_H_
#define _ALLOCATE_H_

#include <stdlib.h>

void *get_spc(size_t num, size_t size);
void *mget_spc(size_t num, size_t size);
void **get_img(size_t wd, size_t ht, size_t size);
void free_img(void **pt);
void *multialloc(size_t s, int d, ...);
void multifree(void *r, int d);

#endif /* _ALLOCATE_H_ */


