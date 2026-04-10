# Linux Command Simulator 🖥️

> Practice Linux commands in the browser. No VM, no risk, no setup.

A virtual Linux terminal running in Flask with an in-memory filesystem. Great for learning and practicing the command line without touching a real system.

## Features

- 100+ simulated Linux commands
- In-memory virtual filesystem (create, edit, delete files/dirs)
- Simulated environment variables and aliases
- `nano` editor support
- Command history
- `neofetch`, `cowsay` and other fun commands

## Run

```bash
git clone https://github.com/Dreadonyx/Linux-command-simulator
cd Linux-command-simulator
pip install flask
python app.py
```

Open `http://localhost:5000`.

## Supported Commands

### Navigation & Files
`pwd` · `ls` · `cd` · `mkdir` · `touch` · `rm` · `cp` · `mv` · `cat` · `ln` · `stat` · `chmod` · `chown` · `find` · `which` · `dirname` · `basename`

### Text Processing
`echo` · `head` · `tail` · `wc` · `grep` · `sort` · `uniq` · `cut` · `tr` · `rev` · `tac` · `awk` · `sed` · `printf` · `less` · `more` · `column` · `paste` · `nl` · `fmt`

### Editors
`nano` · `vim` / `vi`

### Archive & Compression
`tar` · `zip` · `unzip`

### Binary & Forensics
`strings` · `xxd` · `base64` · `file` · `diff` · `md5sum` · `sha256sum` · `nm` · `readelf` · `objdump` · `ldd` · `strace` · `ltrace` · `gdb`

### System & Process
`ps` · `top` / `htop` · `kill` · `df` · `free` · `du` · `vmstat` · `iostat` · `dmesg` · `journalctl` · `lscpu` · `lsblk` · `lsof` · `systemctl` · `service` · `crontab` · `watch` · `nohup` · `at` · `screen` · `tmux` · `lspci` · `lsusb` · `lshw` · `fdisk` · `blkid` · `mount` · `umount` · `uptime` · `uname` · `date` · `cal` · `bc` · `expr`

### User Management
`whoami` · `id` · `passwd` · `useradd` · `userdel` · `usermod` · `groups` · `chgrp` · `sudo` · `su` · `who` · `w` · `last`

### Environment & Shell
`env` · `export` · `alias` · `history` · `type` · `sleep` · `seq` · `tee` · `xargs` · `yes` · `true` · `false` · `jobs` · `bg` · `fg` · `nohup`

### Network
`ping` · `curl` · `wget` · `ssh` · `scp` · `rsync` · `netstat` · `ss` · `ifconfig` · `ip` · `nslookup` · `dig` · `host` · `whois` · `traceroute` · `mtr` · `arp` · `nc` / `netcat` · `ufw` · `iptables` · `nmcli` · `iwconfig`

### Package Management
`apt` / `apt-get` · `pip` / `pip3` · `npm`

### Development & Build
`git` · `python3` / `python` · `node` / `nodejs` · `make` · `gcc` · `g++`

### Utilities
`man` · `clear` · `help` · `exit` · `readlink` · `stat` · `ln` · `tee`

### Fun
`neofetch` · `cowsay`

## Aliases

| Alias | Expands to |
|-------|-----------|
| `ll`  | `ls -la`  |
| `la`  | `ls -a`   |
| `l`   | `ls -CF`  |

## Stack

- Python / Flask
- In-memory virtual filesystem
- Vanilla JS terminal UI
