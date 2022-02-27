all: chatclient.c
	gcc -o chatclient chatclient.c -lpthread

clean:
	rm chatclient
