apptest() {
	networksetup -setairportnetwork en0 MK18F-AppTest qruafj@1257
}
apptest19() {
	networksetup -setairportnetwork en0 MK19F-AppTest qruafj@1257
}
scb5g() {
	networksetup -setairportnetwork en0 SCBMK18F-5G SCB2020dto@
}

ssh-sit() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.163
	unset-ssh-password
}
ssh-uat() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.164
	unset-ssh-password
}
ssh-pp() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.158
	unset-ssh-password
}
ssh-mib-pp1() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.166
	unset-ssh-password
}
ssh-mib-pp2() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.168
	unset-ssh-password
}
ssh-retail-db-preprod() {
	set-ssh-password scbSCB2025##
	sshpass -e ssh root@10.10.230.169
	unset-ssh-password
}
ssh-retail-sit() {
	set-ssh-password
	sshpass -e ssh root@10.21.10.35
	unset-ssh-password
}
ssh-retail-uat() {
	set-ssh-password passmbb1@
	sshpass -e ssh root@10.21.10.15
	unset-ssh-password
}
ssh-bfm-sit() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.157
	unset-ssh-password
}
ssh-apic-1() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.85
	unset-ssh-password
}
ssh-apic-2() {
	set-ssh-password
	sshpass -e ssh root@10.10.230.86
	unset-ssh-password
}

set-ssh-password() {
	# If an argument is provided, use it as the password; otherwise use the default.
	if [ -z "$1" ]; then
		export SSHPASS="password"
	else
		export SSHPASS="$1"
	fi
}

unset-ssh-password() {
	unset SSHPASS
}

scp-sit() {
	set-ssh-password
	sshpass -e scp $1 root@10.10.230.163:/root/docker/$1 
	unset-ssh-password
}
scp-uat() {
	set-ssh-password
	sshpass -e scp $1 root@10.10.230.164:/root/docker/$1
	unset-ssh-password
}
scp-pp() {
	set-ssh-password
	sshpass -e scp $1 root@10.10.230.158:/root/docker/$1
	unset-ssh-password
}
scp-mib-pp() {
	set-ssh-password
	sshpass -e scp $1 root@10.10.230.166:/root/docker/$1
	sshpass -e scp $1 root@10.10.230.168:/root/docker/$1
	unset-ssh-password
}

scp-retail-sit() {
	set-ssh-password
	sshpass -e scp $1 root@10.21.10.35:/home/$1
	unset-ssh-password
}
scp-retail-uat() {
	set-ssh-password
	sshpass -e scp $1 root@10.21.10.15:/home/$1
	unset-ssh-password
}

scp-bfm-sit() {
	set-ssh-password
	sshpass -e scp $1 root@10.10.230.157:~/docker/$1
	unset-ssh-password
}

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"