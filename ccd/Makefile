CC=gcc 
CFLAGS=$(shell pkg-config --cflags aravis-0.8) -g -Wall
#CFLAGS=$(shell pkg-config --cflags aravis-0.8) -O2 -Wall
LDFLAGS=-export-dynamic
LIBS=-lcfitsio -lm $(shell pkg-config --libs aravis-0.8)

SRCS=ccd.c
OBJS= ccd.o

all: ccd

ccd: $(SRCS) $(OBJS)
	$(CC) $(LDFLAGS) $(OBJS) -o ccd $(LIBS)

clean:
	rm $(OBJS) ccd
