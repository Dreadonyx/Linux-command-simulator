# filesystem.py

file_system = {
    "/": {
        "home": {
            "student": {
                "readme.txt": "Welcome to Linux Command Simulator\nThis is a web-based terminal emulator.\nType 'help' to see available commands.",
                "notes.txt": "Meeting notes:\n- Review project timeline\n- Fix bug in login module\n- Deploy to staging server\n- Update documentation",
                "script.sh": "#!/bin/bash\n# Sample script\necho 'Hello World'\ndate\nwhoami",
                "data.csv": "name,age,city\nAlice,25,New York\nBob,30,Los Angeles\nCharlie,35,Chicago\nDiana,28,Houston",
                "config.json": '{"debug": true, "port": 8080, "host": "localhost", "version": "1.0.0"}',
                ".bashrc": "# ~/.bashrc\nexport PATH=$PATH:/usr/local/bin\nalias ll='ls -la'\nalias cls='clear'",
                ".profile": "# ~/.profile\nexport EDITOR=nano\nexport LANG=en_US.UTF-8",
                "Documents": {
                    "report.txt": "Annual Report 2026\n==================\nRevenue: $1.2M\nExpenses: $800K\nProfit: $400K",
                    "todo.txt": "TODO:\n[x] Complete project setup\n[ ] Write unit tests\n[ ] Deploy to production\n[ ] Create backup scripts"
                },
                "Projects": {
                    "app": {
                        "main.py": "#!/usr/bin/env python3\n# Main application\nprint('Hello from Python!')",
                        "requirements.txt": "flask==2.0.0\nrequests==2.28.0\nnumpy==1.23.0"
                    }
                }
            }
        },
        "etc": {
            "passwd": "root:x:0:0:root:/root:/bin/bash\nstudent:x:1000:1000:Student User:/home/student:/bin/bash",
            "hosts": "127.0.0.1   localhost\n::1         localhost\n192.168.1.1 router"
        },
        "var": {
            "log": {
                "syslog": "Jan 22 12:00:00 linux-simulator systemd: Started Session\nJan 22 12:00:01 linux-simulator sshd: Accepted connection\nJan 22 12:00:05 linux-simulator nginx: Server started"
            }
        }
    }
}

current_path = ["/", "home", "student"]

def get_current_dir():
    return "/" + "/".join(current_path[1:])

def navigate_to(path_list):
    node = file_system["/"]
    for p in path_list[1:]:
        node = node[p]
    return node
