
#include <stdio.h>
#include <stdlib.h>
#include "allocate.h"
#include "heap.h"

#define INIT_HEAP_ALLOC 1024

void initialize_heap(struct heap *h)
{
    h->size = 0;
    h->node = (struct heap_node *)mget_spc(INIT_HEAP_ALLOC,sizeof(struct heap_node));

    if(h->node == NULL) {
        printf("\nError: Cannot allocate for heap, size : %d\n",INIT_HEAP_ALLOC);
        h->alloc = 0;
        exit(1);
    }
    else {
        h->alloc = INIT_HEAP_ALLOC;
    }
}


void free_heap(struct heap *h)
{
    free( (void *)h->node);
}


void heap_insert(struct heap *h, struct heap_node *p)
{
    int i,j;

    h->size++;

    if(h->size>h->alloc) {
        h->alloc *= 2;
        h->node = (struct heap_node *)
        realloc((void *)(h->node),(size_t)(h->alloc)*sizeof(struct heap_node));
        if(h->node == NULL) {
            printf("\nError: Cannot allocate for heap, size : %d\n",h->alloc);
            exit(1);
        }
    }

    i = h->size - 1; j = (i-1)/2; /* i is node; j is parent */
    while((i>0)&&(h->node[j].x<p->x)) {
        h->node[i].x = h->node[j].x;
        h->node[i].pt = h->node[j].pt;

        i = j;
        j = (i-1)/2;
    }
    h->node[i].x = p->x;
    h->node[i].pt = p->pt;
}


void get_heap_max(struct heap *h, struct heap_node *p)
{
    if(h->size>0) {
        p->x = h->node[0].x;
        p->pt = h->node[0].pt;

        h->node[0].x = h->node[h->size-1].x;
        h->node[0].pt = h->node[h->size-1].pt;

        h->size--;
        maintain_heap(h,0);
    }
    else {
        p->pt = -1;
        fprintf(stderr,"\nWarning: Extracting from empty heap");
    }
}


void maintain_heap(struct heap *h, int n)
{
    int left,right,max;
    struct heap_node tmp;

    left  = 2*n+1;
    right = 2*n+2;

    if(left < h->size) {
        if(h->node[left].x > h->node[n].x)
        max = left;
        else
        max = n;
    }
    else {
        max = n;
    }

    if(right < h->size) {
        if(h->node[right].x > h->node[max].x)
        max = right;
    }

    if(max != n) {
        tmp.x = h->node[max].x;
        h->node[max].x = h->node[n].x;
        h->node[n].x = tmp.x;

        tmp.pt = h->node[max].pt;
        h->node[max].pt = h->node[n].pt;
        h->node[n].pt = tmp.pt;

        maintain_heap(h,max);
    }
}


