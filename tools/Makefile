all: hp9111a bop

hp9111a: hp9111a.c
	gcc -o hp9111a hp9111a.c -lgpib -lX11
bop: bop.c
	gcc -o bop bop.c -lgpib
clean:
	rm hp9111a bop
