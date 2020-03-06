# Sharing a folder between users

- Create folder in home directory
- Crete shared user group
	sudo groupadd SharedUsers
- Give group permissions to interact with the folder
	sudo chgrp -R SharedUsers /home/data
	sudo chmod -R 2775 /home/data
- Give users permission to interact with folder
	- If user already exists:
		sudo usermod -a -G SharedUsers username
	- If user doesn't exist: 
		sudo useradd -a - G SharedUsers username
