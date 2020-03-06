# Managing users

## 1. Adding a user
- Add user to instance
	sudo adduser <username>
- Login as new user
	sudo su - <username>

## 2. Create .ssh directory
- Run everything below as the new user
	1. mkdir .ssh
	2. chmod 700 .ssh
	3. cd .ssh
	4. touch authorized_keys
	5. chmod 600 authorized_keys

- Copy public key and paste it under "authorized_keys"e

