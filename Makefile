all:
	docker build ./server -t serverim
	docker compose up

.PHONY : client
client:
	docker build ./client/ -t clientim
	docker run -it --name client --network mynet --network-alias client clientim:latest

.PHONY : clean_client
clean_client:
	docker container rm client
	docker rmi clientim

clean:
	docker compose down
	docker rmi loadbalancerim serverim



