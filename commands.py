from filesystem import file_system, current_path, navigate_to, get_current_dir
from datetime import datetime
import platform
import random
import base64 as b64

# Simulated command history
command_history = []

# Simulated environment variables
environment = {
    "USER": "student",
    "HOME": "/home/student",
    "SHELL": "/bin/bash",
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "LANG": "en_US.UTF-8",
    "TERM": "xterm-256color",
    "PWD": "/home/student",
    "EDITOR": "nano",
    "HOSTNAME": "linux-simulator",
}

# Simulated aliases
aliases = {
    "ll": "ls -la",
    "la": "ls -a",
    "l": "ls -CF",
}

# Simulated file permissions (for chmod simulation)
file_permissions = {}

# Simulated process list
processes = [
    {"pid": 1, "name": "systemd", "cpu": "0.1", "user": "root"},
    {"pid": 245, "name": "bash", "cpu": "0.0", "user": "student"},
    {"pid": 892, "name": "python3", "cpu": "2.3", "user": "student"},
    {"pid": 1024, "name": "nginx", "cpu": "0.5", "user": "www-data"},
    {"pid": 1337, "name": "sshd", "cpu": "0.0", "user": "root"},
]

def execute(command):
    parts = command.strip().split()
    if not parts:
        return ""

    # Add to history
    command_history.append(command.strip())

    cmd = parts[0]
    args = parts[1:]

    # Expand aliases
    if cmd in aliases:
        expanded = aliases[cmd].split()
        cmd = expanded[0]
        args = expanded[1:] + args

    try:
        if cmd == "pwd":
            return get_current_dir()

        elif cmd == "ls":
            show_long = "-l" in args or "-la" in args or "-al" in args
            show_all = "-a" in args or "-la" in args or "-al" in args
            node = navigate_to(current_path)
            items = list(node.keys())
            if not show_all:
                items = [i for i in items if not i.startswith(".")]
            else:
                items = [".", ".."] + items
            if show_long:
                lines = []
                for item in items:
                    if item in [".", ".."]:
                        lines.append(f"drwxr-xr-x  2 student student  4096 Jan 20 12:00 {item}")
                    elif isinstance(node.get(item, ""), dict):
                        lines.append(f"drwxr-xr-x  2 student student  4096 Jan 20 12:00 {item}")
                    else:
                        size = len(node.get(item, ""))
                        lines.append(f"-rw-r--r--  1 student student  {size:4d} Jan 20 12:00 {item}")
                return "\n".join(lines)
            return "  ".join(items)

        elif cmd == "cd":
            if not args or args[0] == "~":
                current_path.clear()
                current_path.extend(["/", "home", "student"])
                return ""

            if args[0] == "..":
                if len(current_path) > 1:
                    current_path.pop()
                return ""

            node = navigate_to(current_path)
            if args[0] in node and isinstance(node[args[0]], dict):
                current_path.append(args[0])
                return ""
            return "cd: no such directory"

        elif cmd == "mkdir":
            if not args:
                return "mkdir: missing operand"
            node = navigate_to(current_path)
            for name in args:
                if name.startswith("-"):
                    continue
                node[name] = {}
            return ""

        elif cmd == "touch":
            if not args:
                return "touch: missing file operand"
            node = navigate_to(current_path)
            for name in args:
                if name not in node:
                    node[name] = ""
            return ""

        elif cmd == "cat":
            if not args:
                return "cat: missing file operand"
            node = navigate_to(current_path)
            if args[0] in node:
                content = node[args[0]]
                if isinstance(content, dict):
                    return "cat: Is a directory"
                return content if content else ""
            return "cat: file not found"

        elif cmd == "rm":
            if not args:
                return "rm: missing operand"
            node = navigate_to(current_path)
            target = args[-1] if args[-1] not in ["-r", "-rf", "-f"] else args[0]
            if target.startswith("-"):
                return "rm: missing operand"
            if target not in node:
                return "rm: no such file or directory"
            del node[target]
            return ""

        elif cmd == "cp":
            if len(args) < 2:
                return "cp: missing file operand"
            node = navigate_to(current_path)
            src, dest = args[0], args[1]
            if src not in node:
                return f"cp: cannot stat '{src}': No such file or directory"
            node[dest] = node[src]
            return ""

        elif cmd == "mv":
            if len(args) < 2:
                return "mv: missing file operand"
            node = navigate_to(current_path)
            src, dest = args[0], args[1]
            if src not in node:
                return f"mv: cannot stat '{src}': No such file or directory"
            node[dest] = node[src]
            del node[src]
            return ""

        elif cmd == "echo":
            text = " ".join(args)
            # Handle redirection
            if ">" in args:
                idx = args.index(">")
                content = " ".join(args[:idx])
                if idx + 1 < len(args):
                    filename = args[idx + 1]
                    node = navigate_to(current_path)
                    node[filename] = content
                    return ""
            # Handle variable expansion
            if text.startswith("$"):
                var_name = text[1:]
                return environment.get(var_name, "")
            return text

        elif cmd == "whoami":
            return "student"

        elif cmd == "hostname":
            return "linux-simulator"

        elif cmd == "id":
            return "uid=1000(student) gid=1000(student) groups=1000(student),27(sudo)"

        elif cmd == "date":
            return datetime.now().strftime("%c")

        elif cmd == "uptime":
            hours = random.randint(1, 100)
            mins = random.randint(0, 59)
            users = random.randint(1, 3)
            load = [round(random.uniform(0.1, 2.5), 2) for _ in range(3)]
            return f" {datetime.now().strftime('%H:%M:%S')} up {hours}:{mins:02d},  {users} user,  load average: {load[0]}, {load[1]}, {load[2]}"

        elif cmd == "uname":
            if "-a" in args:
                return "Linux linux-simulator 5.15.0-generic #1 SMP x86_64 GNU/Linux"
            elif "-r" in args:
                return "5.15.0-generic"
            return "Linux"

        elif cmd == "ps":
            lines = ["  PID TTY          TIME CMD"]
            if "-aux" in args or "aux" in args or "-ef" in args:
                lines = ["USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"]
                for p in processes:
                    lines.append(f"{p['user']:8} {p['pid']:5} {p['cpu']:>4}  0.1  12345  1234 ?        Ss   12:00   0:00 {p['name']}")
            else:
                lines.append(f"  245 pts/0    00:00:00 bash")
                lines.append(f"  892 pts/0    00:00:01 python3")
            return "\n".join(lines)

        elif cmd == "kill":
            if not args:
                return "kill: usage: kill [-s sigspec | -n signum | -sigspec] pid | jobspec ..."
            return ""

        elif cmd == "df":
            lines = [
                "Filesystem     1K-blocks    Used Available Use% Mounted on",
                "/dev/sda1       51200000 8234567  42965433  17% /",
                "tmpfs            4096000       0   4096000   0% /dev/shm",
                "/dev/sdb1      102400000 5432100  96967900   6% /home"
            ]
            return "\n".join(lines)

        elif cmd == "free":
            lines = [
                "              total        used        free      shared  buff/cache   available",
                "Mem:        8192000     2048000     4096000      256000     2048000     5632000",
                "Swap:       2048000           0     2048000"
            ]
            return "\n".join(lines)

        elif cmd == "history":
            if not command_history:
                return ""
            lines = []
            for i, hist_cmd in enumerate(command_history[-20:], 1):
                lines.append(f"  {i}  {hist_cmd}")
            return "\n".join(lines)

        elif cmd == "head":
            if not args:
                return "head: missing file operand"
            node = navigate_to(current_path)
            if args[-1] in node:
                content = node[args[-1]]
                if isinstance(content, dict):
                    return "head: error reading: Is a directory"
                lines = content.split("\n")[:10]
                return "\n".join(lines)
            return f"head: cannot open '{args[-1]}' for reading: No such file or directory"

        elif cmd == "tail":
            if not args:
                return "tail: missing file operand"
            node = navigate_to(current_path)
            if args[-1] in node:
                content = node[args[-1]]
                if isinstance(content, dict):
                    return "tail: error reading: Is a directory"
                lines = content.split("\n")[-10:]
                return "\n".join(lines)
            return f"tail: cannot open '{args[-1]}' for reading: No such file or directory"

        elif cmd == "wc":
            if not args:
                return "wc: missing file operand"
            node = navigate_to(current_path)
            if args[-1] in node:
                content = node[args[-1]]
                if isinstance(content, dict):
                    return "wc: Is a directory"
                lines = content.count("\n") + (1 if content else 0)
                words = len(content.split())
                chars = len(content)
                return f"  {lines}  {words}  {chars} {args[-1]}"
            return f"wc: {args[-1]}: No such file or directory"

        elif cmd == "find":
            node = navigate_to(current_path)
            results = []
            def search(n, path):
                for key, val in n.items():
                    full = f"{path}/{key}"
                    results.append(full)
                    if isinstance(val, dict):
                        search(val, full)
            search(node, ".")
            return "\n".join(results) if results else "."

        elif cmd == "grep":
            if len(args) < 2:
                return "Usage: grep PATTERN FILE"
            pattern = args[0]
            filename = args[1]
            node = navigate_to(current_path)
            if filename not in node:
                return f"grep: {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return f"grep: {filename}: Is a directory"
            matches = [line for line in content.split("\n") if pattern in line]
            return "\n".join(matches)

        elif cmd == "man":
            if not args:
                return "What manual page do you want?"
            return f"No manual entry for {args[0]}\nTry 'help' for available commands."

        elif cmd == "which":
            if not args:
                return ""
            known = ["pwd", "ls", "cd", "mkdir", "touch", "rm", "cat", "echo", "whoami",
                     "date", "uname", "clear", "help", "hostname", "id", "uptime", "ps",
                     "kill", "df", "free", "history", "head", "tail", "wc", "find", "grep",
                     "cp", "mv", "man", "which", "exit", "neofetch", "cowsay", "cal",
                     "nano", "strings", "xxd", "base64", "file", "sort", "uniq", "cut",
                     "tr", "rev", "tac", "diff", "chmod", "chown", "env", "export", "alias",
                     "seq", "sleep", "tee", "stat", "ln", "readlink", "dirname", "basename",
                     "md5sum", "sha256sum", "yes", "true", "false", "type",
                     "ping", "curl", "wget", "ssh", "top", "htop", "du", "tar", "zip",
                     "unzip", "awk", "sed", "printf", "sudo", "su", "who", "w", "last",
                     "lscpu", "lsblk", "netstat", "ss", "ifconfig", "ip", "systemctl",
                     "apt", "apt-get", "git", "vim", "vi", "less", "more", "python3",
                     "python", "crontab", "nslookup", "dig", "lsof", "jobs", "bg", "fg",
                     "traceroute", "watch", "nohup", "vmstat", "iostat", "dmesg",
                     "journalctl", "service", "at", "screen", "tmux", "passwd", "useradd",
                     "userdel", "usermod", "groups", "chgrp", "nc", "netcat", "rsync",
                     "scp", "whois", "host", "mtr", "arp", "ufw", "iptables", "nmcli",
                     "iwconfig", "lspci", "lsusb", "lshw", "fdisk", "blkid", "mount",
                     "umount", "make", "gcc", "g++", "pip", "pip3", "node", "nodejs",
                     "npm", "strace", "ltrace", "ldd", "nm", "readelf", "objdump", "gdb",
                     "bc", "expr", "xargs", "column", "paste", "nl", "fmt"]
            if args[0] in known:
                return f"/usr/bin/{args[0]}"
            return ""

        elif cmd == "cal":
            now = datetime.now()
            return f"    {now.strftime('%B %Y')}\nSu Mo Tu We Th Fr Sa\n          1  2  3  4\n 5  6  7  8  9 10 11\n12 13 14 15 16 17 18\n19 20 21 22 23 24 25\n26 27 28 29 30 31"

        elif cmd == "neofetch":
            ascii_art = """
       _,met$$$$$gg.          student@linux-simulator
    ,g$$$$$$$$$$$$$$$P.       ----------------------
  ,g$$P""       \"\"\"Y$$.".     OS: Linux Simulator 1.0
 ,$$P'              `$$$.     Host: Web Browser
',$$P       ,ggs.     `$$b:   Kernel: 5.15.0-generic
`d$$'     ,$P"'   .    $$$    Uptime: 42 hours, 13 mins
 $$P      d$'     ,    $$P    Packages: 1337 (apt)
 $$:      $$.   -    ,d$$'    Shell: bash 5.1.8
 $$;      Y$b._   _,d$P'      Terminal: xterm-256color
 Y$$.    `.`"Y$$$$P"'         CPU: Simulated (1) @ 3.0GHz
 `$$b      "-.__              Memory: 2048MiB / 8192MiB
  `Y$$
   `Y$$.
     `$$b.
       `Y$$b.
         `"Y$b._
             `\"\"\""""
            return ascii_art

        elif cmd == "cowsay":
            text = " ".join(args) if args else "Moo!"
            width = len(text) + 2
            cow = (
                " " + "_" * width + "\n"
                "< " + text + " >\n"
                " " + "-" * width + "\n"
                "        \\   ^__^\n"
                "         \\  (oo)\\_______\n"
                "            (__)\\       )\\/\\\n"
                "                ||----w |\n"
                "                ||     ||"
            )
            return cow

        # ==================== NEW COMMANDS ====================

        elif cmd == "nano":
            if not args:
                return "nano: missing file operand\nUsage: nano [filename]"
            filename = args[0]
            node = navigate_to(current_path)
            # Get existing content or create empty file
            content = ""
            if filename in node:
                if isinstance(node[filename], dict):
                    return f"nano: {filename}: Is a directory"
                content = node[filename]
            else:
                node[filename] = ""
            # Return special nano mode marker with file info
            return f"__nano__:{filename}:{content}"

        elif cmd == "strings":
            if not args:
                return "strings: missing file operand\nUsage: strings [file]"
            node = navigate_to(current_path)
            filename = args[-1]
            if filename.startswith("-"):
                return "strings: missing file operand"
            if filename not in node:
                return f"strings: '{filename}': No such file"
            content = node[filename]
            if isinstance(content, dict):
                return f"strings: '{filename}': Is a directory"
            # Extract printable strings (sequences of 4+ printable chars)
            result = []
            current = ""
            for char in content:
                if char.isprintable() and char != '\n':
                    current += char
                else:
                    if len(current) >= 4:
                        result.append(current)
                    current = ""
            if len(current) >= 4:
                result.append(current)
            return "\n".join(result) if result else ""

        elif cmd == "xxd":
            if not args:
                return "xxd: missing file operand\nUsage: xxd [options] [file]"
            node = navigate_to(current_path)
            filename = args[-1]
            if filename not in node:
                return f"xxd: {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return f"xxd: {filename}: Is a directory"
            # Generate hex dump
            lines = []
            for i in range(0, len(content), 16):
                chunk = content[i:i+16]
                hex_part = " ".join(f"{ord(c):02x}" for c in chunk)
                ascii_part = "".join(c if 32 <= ord(c) < 127 else "." for c in chunk)
                lines.append(f"{i:08x}: {hex_part:<48}  {ascii_part}")
            return "\n".join(lines) if lines else "00000000:"

        elif cmd == "base64":
            if "-d" in args or "--decode" in args:
                # Decode mode
                if len(args) < 2 or args[-1].startswith("-"):
                    return "base64: missing operand"
                try:
                    text = args[-1]
                    decoded = b64.b64decode(text).decode('utf-8')
                    return decoded
                except:
                    return "base64: invalid input"
            else:
                # Encode mode
                if not args:
                    return "base64: missing operand\nUsage: base64 [OPTION] [FILE]"
                node = navigate_to(current_path)
                if args[-1] in node:
                    content = node[args[-1]]
                    if isinstance(content, dict):
                        return "base64: Is a directory"
                    encoded = b64.b64encode(content.encode()).decode()
                    return encoded
                else:
                    # Treat as string to encode
                    encoded = b64.b64encode(args[-1].encode()).decode()
                    return encoded

        elif cmd == "file":
            if not args:
                return "file: missing file operand\nUsage: file [file...]"
            node = navigate_to(current_path)
            results = []
            for filename in args:
                if filename not in node:
                    results.append(f"{filename}: cannot open (No such file or directory)")
                elif isinstance(node[filename], dict):
                    results.append(f"{filename}: directory")
                else:
                    content = node[filename]
                    if not content:
                        results.append(f"{filename}: empty")
                    elif content.startswith("#!/"):
                        results.append(f"{filename}: script, ASCII text executable")
                    elif any(content.startswith(x) for x in ["<!DOCTYPE", "<html", "<?xml"]):
                        results.append(f"{filename}: HTML document, ASCII text")
                    elif content.startswith("{") or content.startswith("["):
                        results.append(f"{filename}: JSON data, ASCII text")
                    else:
                        results.append(f"{filename}: ASCII text")
            return "\n".join(results)

        elif cmd == "sort":
            if not args:
                return "sort: missing file operand"
            node = navigate_to(current_path)
            reverse = "-r" in args
            filename = [a for a in args if not a.startswith("-")][-1] if [a for a in args if not a.startswith("-")] else None
            if not filename:
                return "sort: missing file operand"
            if filename not in node:
                return f"sort: cannot read: {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return "sort: Is a directory"
            lines = content.split("\n")
            sorted_lines = sorted(lines, reverse=reverse)
            return "\n".join(sorted_lines)

        elif cmd == "uniq":
            if not args:
                return "uniq: missing file operand"
            node = navigate_to(current_path)
            count = "-c" in args
            filename = [a for a in args if not a.startswith("-")][-1] if [a for a in args if not a.startswith("-")] else None
            if not filename:
                return "uniq: missing file operand"
            if filename not in node:
                return f"uniq: {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return "uniq: Is a directory"
            lines = content.split("\n")
            result = []
            prev = None
            cnt = 0
            for line in lines:
                if line == prev:
                    cnt += 1
                else:
                    if prev is not None:
                        if count:
                            result.append(f"   {cnt} {prev}")
                        else:
                            result.append(prev)
                    prev = line
                    cnt = 1
            if prev is not None:
                if count:
                    result.append(f"   {cnt} {prev}")
                else:
                    result.append(prev)
            return "\n".join(result)

        elif cmd == "cut":
            if not args:
                return "cut: you must specify a list of bytes, characters, or fields"
            node = navigate_to(current_path)
            delimiter = "\t"
            field = None
            filename = None
            i = 0
            while i < len(args):
                if args[i] == "-d" and i + 1 < len(args):
                    delimiter = args[i + 1]
                    i += 2
                elif args[i] == "-f" and i + 1 < len(args):
                    field = int(args[i + 1]) - 1
                    i += 2
                elif not args[i].startswith("-"):
                    filename = args[i]
                    i += 1
                else:
                    i += 1
            if field is None:
                return "cut: you must specify a list of bytes, characters, or fields"
            if not filename or filename not in node:
                return f"cut: {filename}: No such file or directory" if filename else "cut: missing file operand"
            content = node[filename]
            if isinstance(content, dict):
                return "cut: Is a directory"
            result = []
            for line in content.split("\n"):
                parts = line.split(delimiter)
                if field < len(parts):
                    result.append(parts[field])
                else:
                    result.append("")
            return "\n".join(result)

        elif cmd == "tr":
            if len(args) < 2:
                return "tr: missing operand\nUsage: tr SET1 SET2"
            set1 = args[0]
            set2 = args[1]
            # tr reads from stdin in real use, but we'll just return usage info
            return f"tr: translates '{set1}' to '{set2}'\nNote: In simulator, use echo 'text' | tr '{set1}' '{set2}' pattern is not supported.\nUse: cat file | tr '{set1}' '{set2}' (simulated)"

        elif cmd == "rev":
            if not args:
                return "rev: missing file operand"
            node = navigate_to(current_path)
            filename = args[-1]
            if filename not in node:
                return f"rev: cannot open {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return "rev: Is a directory"
            lines = content.split("\n")
            reversed_lines = [line[::-1] for line in lines]
            return "\n".join(reversed_lines)

        elif cmd == "tac":
            if not args:
                return "tac: missing file operand"
            node = navigate_to(current_path)
            filename = args[-1]
            if filename not in node:
                return f"tac: cannot open '{filename}' for reading: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return "tac: Is a directory"
            lines = content.split("\n")
            return "\n".join(reversed(lines))

        elif cmd == "diff":
            if len(args) < 2:
                return "diff: missing operand after 'diff'\nUsage: diff FILE1 FILE2"
            node = navigate_to(current_path)
            file1, file2 = args[0], args[1]
            if file1 not in node:
                return f"diff: {file1}: No such file or directory"
            if file2 not in node:
                return f"diff: {file2}: No such file or directory"
            content1 = node[file1]
            content2 = node[file2]
            if isinstance(content1, dict) or isinstance(content2, dict):
                return "diff: cannot compare directories"
            if content1 == content2:
                return ""
            lines1 = content1.split("\n")
            lines2 = content2.split("\n")
            result = []
            for i, (l1, l2) in enumerate(zip(lines1, lines2), 1):
                if l1 != l2:
                    result.append(f"{i}c{i}")
                    result.append(f"< {l1}")
                    result.append("---")
                    result.append(f"> {l2}")
            return "\n".join(result) if result else "Files differ"

        elif cmd == "chmod":
            if len(args) < 2:
                return "chmod: missing operand\nUsage: chmod MODE FILE"
            mode = args[0]
            filename = args[1]
            node = navigate_to(current_path)
            if filename not in node:
                return f"chmod: cannot access '{filename}': No such file or directory"
            file_permissions[filename] = mode
            return ""

        elif cmd == "chown":
            if len(args) < 2:
                return "chown: missing operand\nUsage: chown OWNER[:GROUP] FILE"
            return f"chown: changing ownership of '{args[-1]}': Operation not permitted"

        elif cmd == "env":
            lines = [f"{k}={v}" for k, v in environment.items()]
            return "\n".join(sorted(lines))

        elif cmd == "export":
            if not args:
                lines = [f"declare -x {k}=\"{v}\"" for k, v in environment.items()]
                return "\n".join(sorted(lines))
            for arg in args:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    environment[key] = value
            return ""

        elif cmd == "alias":
            if not args:
                lines = [f"alias {k}='{v}'" for k, v in aliases.items()]
                return "\n".join(sorted(lines))
            for arg in args:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    aliases[key] = value.strip("'\"")
            return ""

        elif cmd == "seq":
            if not args:
                return "seq: missing operand"
            try:
                if len(args) == 1:
                    end = int(args[0])
                    return "\n".join(str(i) for i in range(1, end + 1))
                elif len(args) == 2:
                    start, end = int(args[0]), int(args[1])
                    return "\n".join(str(i) for i in range(start, end + 1))
                else:
                    start, step, end = int(args[0]), int(args[1]), int(args[2])
                    return "\n".join(str(i) for i in range(start, end + 1, step))
            except ValueError:
                return "seq: invalid argument"

        elif cmd == "sleep":
            if not args:
                return "sleep: missing operand"
            return f"[Simulated: sleep {args[0]} seconds]"

        elif cmd == "tee":
            if not args:
                return "tee: missing file operand"
            # In real use, tee reads from stdin
            return f"tee: would write stdin to {args[-1]}\n(Use echo 'text' > file in this simulator)"

        elif cmd == "stat":
            if not args:
                return "stat: missing operand"
            node = navigate_to(current_path)
            filename = args[-1]
            if filename not in node:
                return f"stat: cannot statx '{filename}': No such file or directory"
            content = node[filename]
            is_dir = isinstance(content, dict)
            size = 4096 if is_dir else len(content)
            file_type = "directory" if is_dir else "regular file"
            return f"""  File: {filename}
  Size: {size}       Blocks: 8          IO Block: 4096   {file_type}
Device: 802h/2050d   Inode: {random.randint(100000, 999999)}    Links: 1
Access: (0644/-rw-r--r--)  Uid: ( 1000/ student)   Gid: ( 1000/ student)
Access: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.000000000 +0000
Modify: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.000000000 +0000
Change: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.000000000 +0000
 Birth: -"""

        elif cmd == "ln":
            if len(args) < 2:
                return "ln: missing file operand"
            node = navigate_to(current_path)
            src, dest = args[-2], args[-1]
            if src not in node:
                return f"ln: failed to access '{src}': No such file or directory"
            node[dest] = node[src]  # Simulated link (just copy reference)
            return ""

        elif cmd == "readlink":
            if not args:
                return "readlink: missing operand"
            return f"/home/student/{args[-1]}"  # Simulated readlink output

        elif cmd == "dirname":
            if not args:
                return "dirname: missing operand"
            path = args[0]
            if "/" in path:
                return "/".join(path.split("/")[:-1]) or "/"
            return "."

        elif cmd == "basename":
            if not args:
                return "basename: missing operand"
            path = args[0]
            return path.split("/")[-1]

        elif cmd == "md5sum":
            if not args:
                return "md5sum: missing file operand"
            node = navigate_to(current_path)
            results = []
            for filename in args:
                if filename not in node:
                    results.append(f"md5sum: {filename}: No such file or directory")
                elif isinstance(node[filename], dict):
                    results.append(f"md5sum: {filename}: Is a directory")
                else:
                    # Generate fake but consistent hash
                    fake_hash = "".join(f"{ord(c) % 16:x}" for c in (node[filename] + filename)[:32]).ljust(32, '0')
                    results.append(f"{fake_hash}  {filename}")
            return "\n".join(results)

        elif cmd == "sha256sum":
            if not args:
                return "sha256sum: missing file operand"
            node = navigate_to(current_path)
            results = []
            for filename in args:
                if filename not in node:
                    results.append(f"sha256sum: {filename}: No such file or directory")
                elif isinstance(node[filename], dict):
                    results.append(f"sha256sum: {filename}: Is a directory")
                else:
                    # Generate fake but consistent hash
                    fake_hash = "".join(f"{ord(c) % 16:x}" for c in (node[filename] + filename)[:64]).ljust(64, '0')
                    results.append(f"{fake_hash}  {filename}")
            return "\n".join(results)

        elif cmd == "yes":
            text = " ".join(args) if args else "y"
            return "\n".join([text] * 10) + "\n[... would continue indefinitely]"

        elif cmd == "true":
            return ""

        elif cmd == "false":
            return ""

        elif cmd == "type":
            if not args:
                return "type: missing operand"
            cmd_name = args[0]
            builtins = ["cd", "echo", "export", "alias", "exit", "history", "type"]
            if cmd_name in builtins:
                return f"{cmd_name} is a shell builtin"
            if cmd_name in aliases:
                return f"{cmd_name} is aliased to `{aliases[cmd_name]}'"
            known = ["pwd", "ls", "mkdir", "touch", "rm", "cat", "whoami", "date", "uname",
                     "clear", "help", "hostname", "id", "uptime", "ps", "kill", "df", "free",
                     "head", "tail", "wc", "find", "grep", "cp", "mv", "man", "which",
                     "neofetch", "cowsay", "cal", "nano", "strings", "xxd", "base64", "file",
                     "sort", "uniq", "cut", "tr", "rev", "tac", "diff", "chmod", "chown",
                     "env", "seq", "sleep", "tee", "stat", "ln", "readlink", "dirname",
                     "basename", "md5sum", "sha256sum", "yes", "true", "false",
                     "ping", "curl", "wget", "ssh", "top", "htop", "du", "tar", "zip",
                     "unzip", "awk", "sed", "printf", "sudo", "su", "who", "w", "last",
                     "lscpu", "lsblk", "netstat", "ss", "ifconfig", "ip", "systemctl",
                     "apt", "apt-get", "git", "vim", "vi", "less", "more", "python3",
                     "python", "crontab", "nslookup", "dig", "lsof", "jobs", "bg", "fg",
                     "traceroute", "watch", "nohup", "vmstat", "iostat", "dmesg",
                     "journalctl", "service", "at", "screen", "tmux", "passwd", "useradd",
                     "userdel", "usermod", "groups", "chgrp", "nc", "netcat", "rsync",
                     "scp", "whois", "host", "mtr", "arp", "ufw", "iptables", "nmcli",
                     "iwconfig", "lspci", "lsusb", "lshw", "fdisk", "blkid", "mount",
                     "umount", "make", "gcc", "g++", "pip", "pip3", "node", "nodejs",
                     "npm", "strace", "ltrace", "ldd", "nm", "readelf", "objdump", "gdb",
                     "bc", "expr", "xargs", "column", "paste", "nl", "fmt"]
            if cmd_name in known:
                return f"{cmd_name} is /usr/bin/{cmd_name}"
            return f"bash: type: {cmd_name}: not found"

        elif cmd == "ping":
            if not args:
                return "ping: missing host operand\nUsage: ping HOST"
            host = [a for a in args if not a.startswith("-")]
            if not host:
                return "ping: missing host operand"
            host = host[0]
            count = 4
            for a in args:
                if a.startswith("-c") and len(a) > 2:
                    try: count = int(a[2:])
                    except: pass
            if "-c" in args:
                idx = args.index("-c")
                if idx + 1 < len(args):
                    try: count = int(args[idx + 1])
                    except: pass
            lines = [f"PING {host} ({random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}): 56 data bytes"]
            for i in range(1, count + 1):
                ms = round(random.uniform(5, 80), 3)
                lines.append(f"64 bytes from {host}: icmp_seq={i} ttl=64 time={ms} ms")
            avg = round(random.uniform(5, 80), 3)
            lines.append(f"\n--- {host} ping statistics ---")
            lines.append(f"{count} packets transmitted, {count} received, 0% packet loss")
            lines.append(f"rtt min/avg/max/mdev = {avg-2}/{avg}/{avg+5}/1.234 ms")
            return "\n".join(lines)

        elif cmd == "curl":
            if not args:
                return "curl: try 'curl --help' for more information"
            flags = [a for a in args if a.startswith("-")]
            urls = [a for a in args if not a.startswith("-")]
            if not urls:
                return "curl: no URL specified"
            url = urls[0]
            if "-I" in flags or "--head" in flags:
                return f"HTTP/1.1 200 OK\nContent-Type: text/html; charset=utf-8\nServer: nginx/1.18.0\nDate: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}\nContent-Length: 1234"
            if "-o" in flags:
                idx = args.index("-o")
                if idx + 1 < len(args):
                    outfile = args[idx + 1]
                    node = navigate_to(current_path)
                    node[outfile] = f"[Downloaded content from {url}]"
                    return f"  % Total    % Received % Xferd  Average Speed\n100  1234  100  1234    0     0   5432      0  0:00:01\nSaved to: '{outfile}'"
            return f"[Simulated response from {url}]\n<!DOCTYPE html><html><body><h1>Hello from {url}</h1></body></html>"

        elif cmd == "wget":
            if not args:
                return "wget: missing URL\nUsage: wget [options] URL"
            url = [a for a in args if not a.startswith("-")]
            if not url:
                return "wget: missing URL"
            url = url[0]
            filename = url.split("/")[-1] or "index.html"
            node = navigate_to(current_path)
            node[filename] = f"[Downloaded content from {url}]"
            size = random.randint(1000, 99999)
            return f"--{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}--  {url}\nResolving {url.split('/')[2] if '/' in url else url}...\nConnecting... connected.\nHTTP request sent, awaiting response... 200 OK\nLength: {size} ({size//1024}K)\nSaving to: '{filename}'\n\n{filename}   100%[===================>]   {size//1024}K  --.-KB/s    in 0.1s\n\n'{filename}' saved [{size}/{size}]"

        elif cmd == "ssh":
            if not args:
                return "usage: ssh [-p port] [user@]hostname [command]"
            host = [a for a in args if not a.startswith("-")]
            if not host:
                return "ssh: missing hostname"
            host = host[0]
            return f"ssh: connect to host {host} port 22: Connection refused\n(This is a simulator — no real connections are made)"

        elif cmd in ("top", "htop"):
            lines = [
                f"top - {datetime.now().strftime('%H:%M:%S')} up {random.randint(1,99)}:{random.randint(0,59):02d},  1 user,  load average: {round(random.uniform(0,2),2)}, {round(random.uniform(0,2),2)}, {round(random.uniform(0,2),2)}",
                "Tasks:  87 total,   1 running,  86 sleeping,   0 stopped,   0 zombie",
                "%Cpu(s):  2.3 us,  0.7 sy,  0.0 ni, 96.5 id,  0.4 wa,  0.0 hi,  0.1 si",
                "MiB Mem :   8000.0 total,   4096.0 free,   2048.0 used,   1856.0 buff/cache",
                "MiB Swap:   2048.0 total,   2048.0 free,      0.0 used.   5632.0 avail Mem",
                "",
                "  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND",
            ]
            for p in processes:
                cpu = round(random.uniform(0, 5), 1)
                mem = round(random.uniform(0.1, 2.0), 1)
                lines.append(f"{p['pid']:5} {p['user']:8}  20   0   12345   1234    456 S  {cpu:4.1f}  {mem:4.1f}   0:00.01 {p['name']}")
            return "\n".join(lines)

        elif cmd == "du":
            node = navigate_to(current_path)
            if args and not args[0].startswith("-"):
                target = args[0]
                if target not in node:
                    return f"du: cannot access '{target}': No such file or directory"
                content = node[target]
                size = 4 if isinstance(content, dict) else max(1, len(content) // 1024 + 1)
                return f"{size}\t{target}"
            # Show all items in current dir
            lines = []
            total = 0
            for name, val in node.items():
                size = 4 if isinstance(val, dict) else max(1, len(val) // 1024 + 1)
                total += size
                lines.append(f"{size}\t./{name}")
            lines.append(f"{total}\t.")
            return "\n".join(lines)

        elif cmd == "tar":
            if not args:
                return "tar: You must specify one of the '-Acdtrux', '--delete' or '--test-label' options"
            flags = args[0] if args else ""
            if "c" in flags:
                # Create archive
                files = [a for a in args[1:] if not a.startswith("-") and not a.endswith(".tar") and not a.endswith(".gz")]
                archive = next((a for a in args[1:] if a.endswith(".tar") or a.endswith(".gz") or a.endswith(".tar.gz")), None)
                if "-f" in flags or "f" in flags:
                    archive_name = next((a for a in args if a.endswith(".tar") or a.endswith(".gz")), None)
                    if archive_name:
                        node = navigate_to(current_path)
                        node[archive_name] = f"[tar archive containing: {', '.join(files)}]"
                        return ""
                return "tar: specify archive name with -f"
            elif "x" in flags:
                archive = next((a for a in args if a.endswith(".tar") or a.endswith(".gz")), None)
                if not archive:
                    return "tar: specify archive name with -f"
                node = navigate_to(current_path)
                if archive not in node:
                    return f"tar: {archive}: Cannot open: No such file or directory"
                return f"[Simulated: extracted {archive}]"
            elif "t" in flags:
                archive = next((a for a in args if a.endswith(".tar") or a.endswith(".gz")), None)
                if not archive:
                    return "tar: specify archive name with -f"
                node = navigate_to(current_path)
                if archive not in node:
                    return f"tar: {archive}: Cannot open: No such file or directory"
                return f"[Simulated contents of {archive}]"
            return "tar: invalid option"

        elif cmd == "zip":
            if len(args) < 2:
                return "zip: usage: zip [options] zipfile files..."
            zipname = args[0]
            files = args[1:]
            node = navigate_to(current_path)
            missing = [f for f in files if f not in node]
            if missing:
                return f"zip warning: name not matched: {' '.join(missing)}"
            node[zipname] = f"[zip archive containing: {', '.join(files)}]"
            lines = [f"  adding: {f} (deflated 60%)" for f in files]
            return "\n".join(lines)

        elif cmd == "unzip":
            if not args:
                return "unzip: usage: unzip [-opts[modifiers]] file[.zip]"
            zipname = args[-1]
            node = navigate_to(current_path)
            if zipname not in node:
                return f"unzip: cannot find or open {zipname}"
            return f"Archive:  {zipname}\n  inflating: [simulated extraction of {zipname}]"

        elif cmd == "awk":
            if not args:
                return "Usage: awk 'program' [file ...]"
            prog = args[0]
            if len(args) < 2:
                return f"awk: (reading from stdin is not supported in simulator)"
            filename = args[-1]
            node = navigate_to(current_path)
            if filename not in node:
                return f"awk: can't open file {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return f"awk: {filename}: Is a directory"
            # Simple print simulation
            if "print $1" in prog:
                return "\n".join(line.split()[0] for line in content.split("\n") if line.split())
            elif "print $NF" in prog:
                return "\n".join(line.split()[-1] for line in content.split("\n") if line.split())
            elif "print" in prog:
                return content
            return f"[awk: '{prog}' applied to {filename}]"

        elif cmd == "sed":
            if not args:
                return "sed: no script command!\nUsage: sed [options] 'script' [file]"
            script = args[0]
            if len(args) < 2:
                return "sed: no input file\n(stdin not supported in simulator)"
            filename = args[-1]
            node = navigate_to(current_path)
            if filename not in node:
                return f"sed: can't read {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return f"sed: read error on {filename}: Is a directory"
            # Handle s/old/new/ substitution
            if script.startswith("s/"):
                parts = script.split("/")
                if len(parts) >= 3:
                    old, new = parts[1], parts[2]
                    flags = parts[3] if len(parts) > 3 else ""
                    if "g" in flags:
                        result = content.replace(old, new)
                    else:
                        result = "\n".join(line.replace(old, new, 1) for line in content.split("\n"))
                    # If -i flag, modify in place
                    if "-i" in args:
                        node[filename] = result
                        return ""
                    return result
            elif script.startswith("d"):
                # Delete lines matching pattern (simplified)
                return f"[sed: '{script}' applied to {filename}]"
            return f"[sed: '{script}' applied to {filename}]"

        elif cmd == "printf":
            if not args:
                return ""
            fmt = args[0]
            values = args[1:]
            # Simple format substitution
            result = fmt
            for v in values:
                result = result.replace("%s", v, 1).replace("%d", v, 1)
            result = result.replace("\\n", "\n").replace("\\t", "\t")
            return result

        elif cmd == "sudo":
            if not args:
                return "usage: sudo [-u user] command"
            subcmd = args[0]
            if subcmd == "su" or (subcmd == "-" and len(args) > 1):
                return "[sudo] password for student: \nSorry, try again."
            # Re-run the subcommand with a note
            sub_result = execute(" ".join(args))
            return sub_result

        elif cmd == "su":
            user = args[0] if args else "root"
            if user == "root" or user == "-":
                return "Password: \nsu: Authentication failure"
            return f"su: user {user} does not exist"

        elif cmd == "who":
            return f"student  pts/0        {datetime.now().strftime('%Y-%m-%d %H:%M')} (:0)"

        elif cmd == "w":
            lines = [
                f" {datetime.now().strftime('%H:%M:%S')} up {random.randint(1,99)}:{random.randint(0,59):02d},  1 user,  load average: 0.10, 0.08, 0.05",
                "USER     TTY      FROM             LOGIN@   IDLE JCPU   PCPU WHAT",
                f"student  pts/0    :0               {datetime.now().strftime('%H:%M')}    0.00s  0.05s  0.01s bash"
            ]
            return "\n".join(lines)

        elif cmd == "last":
            lines = [
                f"student  pts/0        :0               {datetime.now().strftime('%a %b %d %H:%M')}   still logged in",
                f"student  pts/0        :0               {datetime.now().strftime('%a %b %d')} 09:00 - 17:00  (08:00)",
                f"reboot   system boot  5.15.0-generic   {datetime.now().strftime('%a %b %d')} 08:59",
                "",
                f"wtmp begins {datetime.now().strftime('%a %b %d')} 08:59"
            ]
            return "\n".join(lines)

        elif cmd == "lscpu":
            return (
                "Architecture:            x86_64\n"
                "  CPU op-mode(s):        32-bit, 64-bit\n"
                "  Byte Order:            Little Endian\n"
                "CPU(s):                  4\n"
                "  On-line CPU(s) list:   0-3\n"
                "Vendor ID:               GenuineIntel\n"
                "  Model name:            Intel(R) Core(TM) i5-8250U CPU @ 1.60GHz\n"
                "    CPU MHz:             1600.000\n"
                "    CPU max MHz:         3400.0000\n"
                "    CPU min MHz:         400.0000\n"
                "Caches (sum of all):\n"
                "  L1d:                   128 KiB (4 instances)\n"
                "  L1i:                   128 KiB (4 instances)\n"
                "  L2:                    1 MiB (4 instances)\n"
                "  L3:                    6 MiB (1 instance)"
            )

        elif cmd == "lsblk":
            return (
                "NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT\n"
                "sda      8:0    0    50G  0 disk\n"
                "├─sda1   8:1    0    48G  0 part /\n"
                "└─sda2   8:2    0     2G  0 part [SWAP]\n"
                "sdb      8:16   0   100G  0 disk\n"
                "└─sdb1   8:17   0   100G  0 part /home"
            )

        elif cmd in ("netstat", "ss"):
            lines = [
                "Netid  State      Recv-Q  Send-Q  Local Address:Port    Peer Address:Port",
                "tcp    LISTEN     0       128     0.0.0.0:22           0.0.0.0:*",
                "tcp    LISTEN     0       128     0.0.0.0:80           0.0.0.0:*",
                "tcp    ESTAB      0       0       127.0.0.1:45678      127.0.0.1:5432",
                "udp    UNCONN     0       0       0.0.0.0:68           0.0.0.0:*",
            ]
            return "\n".join(lines)

        elif cmd in ("ifconfig", "ip"):
            if cmd == "ip" and args and args[0] in ("a", "addr", "address"):
                pass  # fall through to same output
            elif cmd == "ip" and args and args[0] not in ("a", "addr", "address", "link", "route", "r"):
                return f"ip: unknown command '{args[0]}'"
            return (
                "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n"
                "        inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255\n"
                "        inet6 fe80::1  prefixlen 64  scopeid 0x20<link>\n"
                "        ether 00:11:22:33:44:55  txqueuelen 1000  (Ethernet)\n"
                "        RX packets 12345  bytes 9876543 (9.4 MiB)\n"
                "        TX packets 6789   bytes 1234567 (1.1 MiB)\n"
                "\n"
                "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536\n"
                "        inet 127.0.0.1  netmask 255.0.0.0\n"
                "        inet6 ::1  prefixlen 128  scopeid 0x10<host>\n"
                "        loop  txqueuelen 1000  (Local Loopback)"
            )

        elif cmd == "systemctl":
            if not args:
                return "systemctl: missing command"
            action = args[0]
            service = args[1] if len(args) > 1 else None
            if action == "status":
                if not service:
                    return "systemctl: missing service name"
                return (
                    f"● {service}.service - {service.capitalize()} Service\n"
                    f"     Loaded: loaded (/lib/systemd/system/{service}.service; enabled)\n"
                    f"     Active: active (running) since {datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')} UTC; 1h ago\n"
                    f"    Process: 1024 ExecStart=/usr/sbin/{service}\n"
                    f"   Main PID: 1024 ({service})\n"
                    f"      Tasks: 2 (limit: 4915)\n"
                    f"     Memory: 4.5M"
                )
            elif action in ("start", "stop", "restart", "enable", "disable", "reload"):
                if not service:
                    return f"systemctl {action}: missing service name"
                return ""  # success silently
            elif action == "list-units":
                return (
                    "  UNIT                     LOAD   ACTIVE SUB     DESCRIPTION\n"
                    "  nginx.service            loaded active running A high performance web server\n"
                    "  sshd.service             loaded active running OpenSSH server daemon\n"
                    "  cron.service             loaded active running Regular background program processing\n"
                    "\nLEGEND: LOAD=Reflects whether the unit definition was properly loaded.\n"
                    "        ACTIVE=The high-level unit activation state."
                )
            return f"systemctl: unknown command '{action}'"

        elif cmd in ("apt", "apt-get"):
            if not args:
                return f"{cmd}: missing command\nUsage: {cmd} [options] command"
            action = args[0]
            packages = args[1:]
            if action == "update":
                return (
                    "Hit:1 http://archive.ubuntu.com/ubuntu focal InRelease\n"
                    "Get:2 http://archive.ubuntu.com/ubuntu focal-updates InRelease\n"
                    "Fetched 1,234 kB in 2s (617 kB/s)\n"
                    "Reading package lists... Done"
                )
            elif action in ("install", "reinstall"):
                if not packages:
                    return f"{cmd}: {action}: no packages specified"
                pkg_list = " ".join(packages)
                return (
                    f"Reading package lists... Done\n"
                    f"Building dependency tree... Done\n"
                    f"The following NEW packages will be installed:\n"
                    f"  {pkg_list}\n"
                    f"0 upgraded, {len(packages)} newly installed, 0 to remove and 0 not upgraded.\n"
                    f"[Simulated: {pkg_list} installed successfully]"
                )
            elif action in ("remove", "purge"):
                if not packages:
                    return f"{cmd}: {action}: no packages specified"
                return f"[Simulated: {' '.join(packages)} removed]"
            elif action in ("upgrade", "full-upgrade", "dist-upgrade"):
                return "Reading package lists... Done\nCalculating upgrade... Done\n0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded."
            elif action == "search":
                q = " ".join(packages)
                return f"Sorting... Done\nFull-text search... Done\n{q}/focal 1.0-1 amd64\n  Package matching '{q}'"
            elif action == "show":
                pkg = packages[0] if packages else "?"
                return (
                    f"Package: {pkg}\n"
                    f"Version: 1.0-1\n"
                    f"Priority: optional\n"
                    f"Section: utils\n"
                    f"Installed-Size: 1024\n"
                    f"Maintainer: Ubuntu Developers\n"
                    f"Description: Simulated package '{pkg}'"
                )
            return f"{cmd}: invalid operation {action}"

        elif cmd == "git":
            if not args:
                return (
                    "usage: git [-v | --version] [-h | --help] [-C <path>] [-c <name>=<value>]\n"
                    "           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]\n"
                    "           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]\n"
                    "           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]\n"
                    "           [--super-prefix=<path>] [--config-env=<name>=<envvar>]\n"
                    "           <command> [<args>]\n"
                )
            subcmd = args[0]
            rest = args[1:]
            if subcmd == "init":
                node = navigate_to(current_path)
                node[".git"] = {"HEAD": "ref: refs/heads/main", "config": "[core]\n\trepositoryformatversion = 0"}
                return f"Initialized empty Git repository in {get_current_dir()}/.git/"
            elif subcmd == "status":
                return (
                    "On branch main\n\n"
                    "No commits yet\n\n"
                    "nothing to commit (create/copy files and use \"git add\" to track)"
                )
            elif subcmd == "add":
                return ""
            elif subcmd == "commit":
                msg = "Initial commit"
                if "-m" in rest:
                    idx = rest.index("-m")
                    if idx + 1 < len(rest):
                        msg = rest[idx + 1].strip("'\"")
                hash_ = "".join(random.choices("0123456789abcdef", k=7))
                return f"[main (root-commit) {hash_}] {msg}\n 1 file changed, 0 insertions(+), 0 deletions(-)"
            elif subcmd == "log":
                hash_ = "".join(random.choices("0123456789abcdef", k=40))
                return (
                    f"commit {hash_}\n"
                    f"Author: student <student@linux-simulator>\n"
                    f"Date:   {datetime.now().strftime('%a %b %d %H:%M:%S %Y +0000')}\n\n"
                    f"    Initial commit"
                )
            elif subcmd == "clone":
                url = rest[0] if rest else "<url>"
                dirname = url.split("/")[-1].replace(".git", "")
                node = navigate_to(current_path)
                node[dirname] = {".git": {}, "README.md": "# " + dirname}
                return f"Cloning into '{dirname}'...\nremote: Counting objects: 3, done.\nReceiving objects: 100% (3/3), done."
            elif subcmd in ("pull", "fetch", "push"):
                return f"[Simulated: git {subcmd}]\nEverything up-to-date."
            elif subcmd == "branch":
                if rest:
                    return ""
                return "* main"
            elif subcmd == "checkout":
                branch = rest[0] if rest else "main"
                if "-b" in rest:
                    idx = rest.index("-b")
                    branch = rest[idx + 1] if idx + 1 < len(rest) else "new-branch"
                    return f"Switched to a new branch '{branch}'"
                return f"Switched to branch '{branch}'"
            elif subcmd == "diff":
                return "(no changes)"
            elif subcmd in ("stash", "merge", "rebase", "tag", "remote", "reset"):
                return f"[Simulated: git {subcmd} {' '.join(rest)}]"
            return f"git: '{subcmd}' is not a git command. See 'git --help'."

        elif cmd in ("vim", "vi"):
            if not args:
                return (
                    "VIM - Vi IMproved (simulated)\n\n"
                    "type  :q<Enter>               to exit\n"
                    "type  :help<Enter>             for help\n"
                    "(This is a simulator — use nano for editing files)"
                )
            filename = args[-1]
            node = navigate_to(current_path)
            if filename not in node:
                node[filename] = ""
            return f"[vim: '{filename}' opened in simulated mode]\nThis simulator does not support interactive vim.\nUse nano {filename} instead."

        elif cmd in ("less", "more"):
            if not args:
                return f"{cmd}: missing file operand"
            node = navigate_to(current_path)
            filename = args[-1]
            if filename not in node:
                return f"{cmd}: {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return f"{cmd}: {filename}: Is a directory"
            return content

        elif cmd == "python3" or cmd == "python":
            if not args:
                return (
                    f"Python 3.10.6 (simulated)\n"
                    f"Type \"help\", \"copyright\", \"credits\" or \"license\" for more information.\n"
                    f">>> (interactive mode not supported in simulator)"
                )
            if args[0] == "-c" and len(args) > 1:
                code = args[1]
                # Very limited eval for simple print statements
                if code.startswith("print(") and code.endswith(")"):
                    inner = code[6:-1].strip("'\"")
                    return inner
                return f"[Simulated: python3 -c '{code}']"
            filename = args[0]
            node = navigate_to(current_path)
            if filename not in node:
                return f"python3: can't open file '{filename}': [Errno 2] No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return f"python3: '{filename}': Is a directory"
            return f"[Simulated: running {filename}]"

        elif cmd == "crontab":
            if "-l" in args:
                return "# no crontab for student"
            elif "-e" in args:
                return "[Simulated: crontab editor opened]\nUse 'crontab -l' to list jobs."
            elif "-r" in args:
                return ""
            return "usage: crontab [-u user] [-l | -r | -e] [-i]"

        elif cmd in ("nslookup", "dig"):
            if not args:
                return f"{cmd}: missing hostname"
            host = [a for a in args if not a.startswith("-")]
            if not host:
                return f"{cmd}: missing hostname"
            host = host[0]
            ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            if cmd == "nslookup":
                return f"Server:\t\t8.8.8.8\nAddress:\t8.8.8.8#53\n\nNon-authoritative answer:\nName:\t{host}\nAddress: {ip}"
            else:
                return (
                    f"; <<>> DiG 9.16.1 <<>> {host}\n"
                    f";; QUESTION SECTION:\n;{host}.\t\t\tIN\tA\n\n"
                    f";; ANSWER SECTION:\n{host}.\t\t300\tIN\tA\t{ip}\n\n"
                    f";; Query time: {random.randint(1,50)} msec\n"
                    f";; SERVER: 8.8.8.8#53(8.8.8.8)"
                )

        elif cmd == "lsof":
            lines = [
                "COMMAND   PID     USER   FD   TYPE DEVICE SIZE/OFF NODE NAME",
                f"systemd     1     root  cwd    DIR    8,1     4096    2 /",
                f"bash      245  student  cwd    DIR    8,1     4096 1234 {get_current_dir()}",
                f"python3   892  student  cwd    DIR    8,1     4096 1234 {get_current_dir()}",
                f"nginx    1024 www-data    3u  IPv4  12345      0t0  TCP *:80 (LISTEN)",
                f"sshd     1337     root    3u  IPv4  12346      0t0  TCP *:22 (LISTEN)",
            ]
            if args:
                # filter by name if given
                needle = args[-1]
                lines = [lines[0]] + [l for l in lines[1:] if needle in l]
            return "\n".join(lines)

        elif cmd in ("jobs", "bg", "fg"):
            return "[No active jobs]"

        elif cmd == "traceroute":
            if not args:
                return "traceroute: missing host operand"
            host = [a for a in args if not a.startswith("-")]
            if not host:
                return "traceroute: missing host operand"
            host = host[0]
            lines = [f"traceroute to {host}, 30 hops max, 60 byte packets"]
            for i in range(1, 6):
                ms1 = round(random.uniform(1, 50), 3)
                ms2 = round(random.uniform(1, 50), 3)
                ms3 = round(random.uniform(1, 50), 3)
                ip = f"{10}.{random.randint(0,255)}.{random.randint(0,255)}.{i}"
                lines.append(f" {i}  {ip}  {ms1} ms  {ms2} ms  {ms3} ms")
            lines.append(f" 6  {host}  {round(random.uniform(10,100),3)} ms")
            return "\n".join(lines)

        # ==================== ADDITIONAL COMMANDS ====================

        elif cmd == "watch":
            if not args:
                return "watch: missing command\nUsage: watch [options] command"
            interval = 2
            if "-n" in args:
                idx = args.index("-n")
                if idx + 1 < len(args):
                    try: interval = float(args[idx + 1])
                    except: pass
            subcmd = " ".join(a for a in args if not a.startswith("-") and a != str(interval))
            return f"[Simulated: watch -n {interval} {subcmd}]\n(Repeating every {interval}s — not interactive in simulator)\n\n" + execute(subcmd)

        elif cmd == "nohup":
            if not args:
                return "nohup: missing operand\nUsage: nohup COMMAND [ARG]..."
            return f"nohup: appending output to 'nohup.out'\n[Simulated: {' '.join(args)} running immune to hangups]"

        elif cmd == "vmstat":
            return (
                "procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----\n"
                " r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st\n"
                " 1  0      0 4096000 102400 2048000    0    0    12    8  234  456  3  1 96  0  0"
            )

        elif cmd == "iostat":
            return (
                f"Linux 5.15.0-generic   {datetime.now().strftime('%m/%d/%Y')}   _x86_64_   (4 CPU)\n\n"
                "avg-cpu:  %user   %nice %system %iowait  %steal   %idle\n"
                "           2.34    0.00    0.78    0.12    0.00   96.76\n\n"
                "Device             tps    kB_read/s    kB_wrtn/s    kB_read    kB_wrtn\n"
                "sda               5.42        82.34        34.12     123456      51234\n"
                "sdb               0.12         1.23         0.45       1234        456"
            )

        elif cmd == "dmesg":
            lines = [
                f"[    0.000000] Linux version 5.15.0-generic",
                f"[    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz root=/dev/sda1",
                f"[    0.100000] BIOS-provided physical RAM map:",
                f"[    1.234567] PCI: Using configuration type 1 for base access",
                f"[    2.345678] NET: Registered PF_INET protocol family",
                f"[    3.456789] eth0: renamed from veth1234",
                f"[    5.678901] EXT4-fs (sda1): mounted filesystem",
                f"[   10.123456] systemd[1]: Reached target Basic System.",
            ]
            if "-T" in args:
                lines = [f"[{datetime.now().strftime('%a %b %d %H:%M:%S %Y')}] " + l.split("] ", 1)[1] for l in lines]
            return "\n".join(lines)

        elif cmd == "journalctl":
            if "-u" in args:
                idx = args.index("-u")
                unit = args[idx + 1] if idx + 1 < len(args) else "unknown"
                return (
                    f"-- Journal begins at {datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')} --\n"
                    f"{datetime.now().strftime('%b %d %H:%M:%S')} linux-simulator {unit}[1024]: Starting {unit}...\n"
                    f"{datetime.now().strftime('%b %d %H:%M:%S')} linux-simulator {unit}[1024]: {unit} started successfully.\n"
                    f"{datetime.now().strftime('%b %d %H:%M:%S')} linux-simulator systemd[1]: Started {unit}.service."
                )
            if "-f" in args:
                return f"-- Journal follows --\n{datetime.now().strftime('%b %d %H:%M:%S')} linux-simulator kernel: [Simulated live logs]"
            return (
                f"-- Logs begin at {datetime.now().strftime('%a %Y-%m-%d %H:%M:%S')} --\n"
                f"{datetime.now().strftime('%b %d %H:%M:%S')} linux-simulator systemd[1]: Started Session 1 of user student.\n"
                f"{datetime.now().strftime('%b %d %H:%M:%S')} linux-simulator sshd[1337]: Server listening on 0.0.0.0 port 22.\n"
                f"{datetime.now().strftime('%b %d %H:%M:%S')} linux-simulator kernel: eth0: Link is Up - 1Gbps/Full"
            )

        elif cmd == "service":
            if not args:
                return "Usage: service <service> <command>"
            if len(args) < 2:
                return f"Usage: service {args[0]} <command>"
            svc, action = args[0], args[1]
            if action == "status":
                state = random.choice(["running", "stopped"])
                return f" * {svc} is {state}"
            elif action in ("start", "stop", "restart", "reload"):
                return f" * {action.capitalize()}ing {svc}..."
            return f"service: invalid action '{action}'"

        elif cmd == "at":
            if not args:
                return "Garbled time\nUsage: at [-f file] TIME"
            time_spec = " ".join(args)
            return f"warning: commands will be executed using /bin/sh\njob 1 at {datetime.now().strftime('%a %b %d %H:%M:%S %Y')}\n[Simulated: job scheduled for {time_spec}]"

        elif cmd == "screen":
            if not args:
                return "[Simulated: new screen session created]\nPress Ctrl+a d to detach (not interactive in simulator)"
            if args[0] == "-ls":
                return "No Sockets found in /run/screen/S-student."
            if args[0] in ("-d", "-r"):
                return "No screen session found."
            return f"[Simulated: screen {' '.join(args)}]"

        elif cmd == "tmux":
            if not args:
                return "[Simulated: new tmux session]\n(Interactive mode not supported in simulator)"
            subcmd = args[0]
            if subcmd == "ls" or subcmd == "list-sessions":
                return "no server running on /tmp/tmux-1000/default"
            if subcmd in ("new", "new-session"):
                return "[Simulated: new tmux session created]"
            if subcmd in ("attach", "a"):
                return "no sessions"
            return f"[Simulated: tmux {' '.join(args)}]"

        elif cmd == "passwd":
            if args and args[0] != "student":
                return f"passwd: user '{args[0]}' does not exist"
            return "Changing password for student.\nCurrent password: \nNew password: \nRetype new password: \n[Simulated: password unchanged in simulator]"

        elif cmd == "useradd":
            if not args:
                return "Usage: useradd [options] LOGIN"
            user = [a for a in args if not a.startswith("-")]
            if not user:
                return "useradd: no username specified"
            return f"[Simulated: user '{user[0]}' created]"

        elif cmd == "userdel":
            if not args:
                return "Usage: userdel [options] LOGIN"
            return f"[Simulated: user '{args[-1]}' deleted]"

        elif cmd == "usermod":
            if not args:
                return "Usage: usermod [options] LOGIN"
            return f"[Simulated: user '{args[-1]}' modified]"

        elif cmd == "groups":
            user = args[0] if args else "student"
            return f"{user} : {user} sudo adm dialout cdrom plugdev lpadmin"

        elif cmd == "chgrp":
            if len(args) < 2:
                return "chgrp: missing operand\nUsage: chgrp GROUP FILE"
            return ""

        elif cmd in ("nc", "netcat"):
            if not args:
                return "usage: nc [-options] hostname port\n       nc -l [-options] [hostname] port"
            if "-l" in args:
                port = [a for a in args if a.isdigit()]
                p = port[0] if port else "?"
                return f"[Simulated: listening on port {p}]\n(Not interactive in simulator)"
            hosts = [a for a in args if not a.startswith("-") and not a.isdigit()]
            ports = [a for a in args if a.isdigit()]
            if hosts and ports:
                return f"[Simulated: connected to {hosts[0]}:{ports[0]}]\n(Not interactive in simulator)"
            return "nc: missing hostname or port"

        elif cmd == "rsync":
            if len(args) < 2:
                return "rsync: missing destination\nUsage: rsync [options] SRC DEST"
            src, dest = args[-2], args[-1]
            return (
                f"sending incremental file list\n"
                f"{src}\n\n"
                f"sent 1,234 bytes  received 35 bytes  1,846.00 bytes/sec\n"
                f"total size is 1,200  speedup is 0.95"
            )

        elif cmd == "scp":
            if len(args) < 2:
                return "usage: scp [-r] source destination"
            return f"[Simulated: scp {' '.join(args)}]\n(No real transfer in simulator)"

        elif cmd == "whois":
            if not args:
                return "whois: missing domain"
            domain = args[0]
            return (
                f"Domain Name: {domain.upper()}\n"
                f"Registry Domain ID: SIMULATED\n"
                f"Registrar: Example Registrar, Inc.\n"
                f"Creation Date: 2000-01-01T00:00:00Z\n"
                f"Updated Date: {datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
                f"Expiry Date: 2030-01-01T00:00:00Z\n"
                f"Name Server: ns1.example.com\n"
                f"Name Server: ns2.example.com"
            )

        elif cmd == "host":
            if not args:
                return "Usage: host [-t type] name [server]"
            target = [a for a in args if not a.startswith("-")]
            if not target:
                return "host: missing name"
            target = target[0]
            ip = f"{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
            return f"{target} has address {ip}\n{target} mail is handled by 10 mail.{target}."

        elif cmd == "mtr":
            if not args:
                return "mtr: missing host operand"
            host = [a for a in args if not a.startswith("-")]
            if not host:
                return "mtr: missing host operand"
            host = host[0]
            lines = [
                f"Start: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')}",
                f"HOST: linux-simulator              Loss%   Snt   Last   Avg  Best  Wrst StDev",
            ]
            for i in range(1, 6):
                ip = f"10.0.{i}.1"
                loss = 0
                avg = round(random.uniform(1, 50), 1)
                lines.append(f"  {i}.|-- {ip:<24} {loss:.1f}%    10   {avg}  {avg}  {avg-1}  {avg+2}   0.5")
            lines.append(f"  6.|-- {host:<24} 0.0%    10   {round(random.uniform(10,100),1)}  ...")
            return "\n".join(lines)

        elif cmd == "arp":
            if "-n" in args or not args:
                return (
                    "Address                  HWtype  HWaddress           Flags Mask            Iface\n"
                    "192.168.1.1              ether   aa:bb:cc:dd:ee:ff   C                     eth0\n"
                    "192.168.1.2              ether   11:22:33:44:55:66   C                     eth0"
                )
            return (
                "linux-simulator.local (192.168.1.100) at <incomplete> on eth0\n"
                "_gateway (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0"
            )

        elif cmd == "ufw":
            if not args:
                return "Usage: ufw COMMAND\nCommands: enable|disable|status|allow|deny|delete|reset"
            action = args[0]
            if action == "status":
                return "Status: inactive"
            elif action == "enable":
                return "Firewall is active and enabled on system startup"
            elif action == "disable":
                return "Firewall stopped and disabled on system startup"
            elif action in ("allow", "deny"):
                rule = " ".join(args[1:]) if len(args) > 1 else "?"
                return f"Rule {'added' if action == 'allow' else 'added (deny)'}: {rule}"
            return f"ufw: unknown command '{action}'"

        elif cmd == "iptables":
            if not args or "-L" in args:
                return (
                    "Chain INPUT (policy ACCEPT)\n"
                    "target     prot opt source               destination\n"
                    "ACCEPT     all  --  anywhere             anywhere    state RELATED,ESTABLISHED\n\n"
                    "Chain FORWARD (policy DROP)\n"
                    "target     prot opt source               destination\n\n"
                    "Chain OUTPUT (policy ACCEPT)\n"
                    "target     prot opt source               destination"
                )
            return f"[Simulated: iptables {' '.join(args)}]"

        elif cmd == "nmcli":
            if not args:
                return "Usage: nmcli [OPTIONS] OBJECT { COMMAND | help }"
            obj = args[0]
            if obj in ("d", "device"):
                return (
                    "DEVICE  TYPE      STATE      CONNECTION\n"
                    "eth0    ethernet  connected  Wired connection 1\n"
                    "lo      loopback  unmanaged  --"
                )
            elif obj in ("c", "connection"):
                return (
                    "NAME                UUID                                  TYPE      DEVICE\n"
                    "Wired connection 1  12345678-1234-1234-1234-123456789abc  ethernet  eth0"
                )
            elif obj in ("g", "general"):
                return "STATE      CONNECTIVITY  WIFI-HW  WIFI     WWAN-HW  WWAN\nconnected  full          enabled  enabled  enabled  enabled"
            return f"[Simulated: nmcli {' '.join(args)}]"

        elif cmd == "iwconfig":
            return (
                "wlan0     IEEE 802.11  ESSID:\"MyNetwork\"\n"
                "          Mode:Managed  Frequency:2.437 GHz  Access Point: AA:BB:CC:DD:EE:FF\n"
                "          Bit Rate=54 Mb/s   Tx-Power=20 dBm\n"
                "          Link Quality=70/70  Signal level=-40 dBm  Noise level=-95 dBm\n"
                "          Rx invalid nwid:0  Rx invalid crypt:0  Rx invalid frag:0\n\n"
                "lo        no wireless extensions."
            )

        elif cmd == "lspci":
            return (
                "00:00.0 Host bridge: Intel Corporation 8th Gen Core Processor Host Bridge/DRAM (rev 07)\n"
                "00:02.0 VGA compatible controller: Intel Corporation UHD Graphics 620\n"
                "00:14.0 USB controller: Intel Corporation Sunrise Point-LP USB 3.0 xHCI Controller\n"
                "00:1f.2 Memory controller: Intel Corporation Sunrise Point-LP PMC\n"
                "01:00.0 Network controller: Intel Corporation Wireless 8265 / 8275\n"
                "02:00.0 Ethernet controller: Realtek Semiconductor RTL8111/8168/8411 Gigabit Ethernet"
            )

        elif cmd == "lsusb":
            return (
                "Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub\n"
                "Bus 001 Device 003: ID 8087:0a2b Intel Corp. Bluetooth wireless interface\n"
                "Bus 001 Device 002: ID 04f2:b5ce Chicony Electronics Co., Ltd Integrated Camera\n"
                "Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub"
            )

        elif cmd == "lshw":
            return (
                "linux-simulator\n"
                "    description: Computer\n"
                "    product: Simulated Machine\n"
                "  *-core\n"
                "       description: Motherboard\n"
                "     *-cpu\n"
                "          description: CPU\n"
                "          product: Intel(R) Core(TM) i5-8250U CPU @ 1.60GHz\n"
                "          capacity: 3400MHz\n"
                "     *-memory\n"
                "          description: System Memory\n"
                "          size: 8GiB\n"
                "     *-display\n"
                "          description: VGA compatible controller\n"
                "          product: UHD Graphics 620\n"
                "     *-network\n"
                "          description: Ethernet interface\n"
                "          logical name: eth0\n"
                "          capacity: 1Gbit/s"
            )

        elif cmd == "fdisk":
            if "-l" in args:
                return (
                    "Disk /dev/sda: 50 GiB, 53687091200 bytes, 104857600 sectors\n"
                    "Units: sectors of 1 * 512 = 512 bytes\n\n"
                    "Device     Boot    Start       End   Sectors  Size Id Type\n"
                    "/dev/sda1  *        2048  98566143  98564096   47G 83 Linux\n"
                    "/dev/sda2       98566144 104857599   6291456    3G 82 Linux swap\n\n"
                    "Disk /dev/sdb: 100 GiB, 107374182400 bytes, 209715200 sectors\n"
                    "Device     Boot Start       End   Sectors  Size Id Type\n"
                    "/dev/sdb1        2048 209715199 209713152  100G 83 Linux"
                )
            return "fdisk: requires root privileges or use -l to list"

        elif cmd == "blkid":
            return (
                '/dev/sda1: UUID="a1b2c3d4-e5f6-7890-abcd-ef1234567890" TYPE="ext4" PARTUUID="12345678-01"\n'
                '/dev/sda2: UUID="b2c3d4e5-f6a7-8901-bcde-f01234567891" TYPE="swap" PARTUUID="12345678-02"\n'
                '/dev/sdb1: UUID="c3d4e5f6-a7b8-9012-cdef-012345678912" TYPE="ext4" PARTUUID="87654321-01"'
            )

        elif cmd == "mount":
            if len(args) >= 2:
                return f"[Simulated: mounted {args[0]} at {args[1]}]"
            return (
                "sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)\n"
                "proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)\n"
                "/dev/sda1 on / type ext4 (rw,relatime,errors=remount-ro)\n"
                "/dev/sdb1 on /home type ext4 (rw,relatime)\n"
                "tmpfs on /tmp type tmpfs (rw,nosuid,nodev)"
            )

        elif cmd == "umount":
            if not args:
                return "umount: missing operand"
            return f"[Simulated: unmounted {args[-1]}]"

        elif cmd == "make":
            target = args[0] if args else "all"
            if target == "clean":
                return "rm -f *.o *.out\n[Simulated: cleaned build artifacts]"
            return (
                f"gcc -Wall -o {target} {target}.c\n"
                f"[Simulated: built target '{target}' successfully]"
            )

        elif cmd in ("gcc", "g++"):
            if not args:
                return f"{cmd}: no input files"
            src = [a for a in args if not a.startswith("-")]
            out = None
            if "-o" in args:
                idx = args.index("-o")
                if idx + 1 < len(args):
                    out = args[idx + 1]
            if not src:
                return f"{cmd}: no input files"
            outname = out or "a.out"
            node = navigate_to(current_path)
            if src[0] not in node:
                return f"{cmd}: {src[0]}: No such file or directory"
            node[outname] = f"[compiled binary from {src[0]}]"
            return f"[Simulated: compiled {src[0]} -> {outname}]"

        elif cmd in ("pip", "pip3"):
            if not args:
                return f"{cmd}: missing command\nUsage: {cmd} <command> [options]"
            action = args[0]
            packages = args[1:]
            if action == "install":
                if not packages:
                    return f"{cmd}: install requires at least 1 argument"
                pkg = packages[0].split("==")[0]
                ver = packages[0].split("==")[1] if "==" in packages[0] else "latest"
                return (
                    f"Collecting {pkg}\n"
                    f"  Downloading {pkg}-{ver if ver != 'latest' else '1.0.0'}.tar.gz\n"
                    f"Installing collected packages: {pkg}\n"
                    f"Successfully installed {pkg}"
                )
            elif action in ("uninstall", "remove"):
                pkg = packages[0] if packages else "?"
                return f"Found existing installation: {pkg}\nSuccessfully uninstalled {pkg}"
            elif action == "list":
                return (
                    "Package           Version\n"
                    "----------------- -------\n"
                    "pip               23.0.1\n"
                    "setuptools        67.6.0\n"
                    "requests          2.28.2\n"
                    "numpy             1.24.2"
                )
            elif action in ("show", "info"):
                pkg = packages[0] if packages else "?"
                return f"Name: {pkg}\nVersion: 1.0.0\nSummary: Simulated package\nLocation: /usr/lib/python3/dist-packages"
            elif action == "freeze":
                return "requests==2.28.2\nnumpy==1.24.2\nsetuptools==67.6.0"
            return f"{cmd}: unknown command '{action}'"

        elif cmd in ("node", "nodejs"):
            if not args:
                return "Welcome to Node.js v18.12.1 (simulated)\n(interactive mode not supported in simulator)"
            if args[0] == "-e":
                code = args[1] if len(args) > 1 else ""
                if "console.log" in code:
                    inner = code.split("console.log(")[1].rstrip(")").strip("'\"")
                    return inner
                return f"[Simulated: node -e '{code}']"
            filename = args[0]
            node_fs = navigate_to(current_path)
            if filename not in node_fs:
                return f"node: can't open file '{filename}': [Errno 2] No such file or directory"
            return f"[Simulated: running {filename} with Node.js]"

        elif cmd == "npm":
            if not args:
                return "Usage: npm <command>\nwhere <command> is one of: install, run, start, test, init, ..."
            action = args[0]
            if action == "install":
                pkg = args[1] if len(args) > 1 else None
                if pkg:
                    return f"added 1 package in 1s\n\n1 package is looking for funding\n  run `npm fund` for details"
                return "added 234 packages in 5s\n\n30 packages are looking for funding\n  run `npm fund` for details"
            elif action in ("start", "test", "run"):
                script = args[1] if action == "run" and len(args) > 1 else action
                return f"> simulate@1.0.0 {script}\n> node index.js\n\n[Simulated: npm {action}]"
            elif action == "init":
                return "This utility will walk you through creating a package.json file.\n[Simulated: package.json created]"
            elif action == "list" or action == "ls":
                return "simulate@1.0.0\n└── express@4.18.2"
            return f"npm: unknown command '{action}'"

        elif cmd == "strace":
            if not args:
                return "strace: must have PROG [ARGS] or -p PID"
            if "-p" in args:
                idx = args.index("-p")
                pid = args[idx + 1] if idx + 1 < len(args) else "?"
                return (
                    f"strace: attach: ptrace(PTRACE_SEIZE, {pid}): [Simulated]\n"
                    f"read(0, \"\", 8192)                       = 0\n"
                    f"write(1, \"output\", 6)                   = 6\n"
                    f"+++ exited with 0 +++"
                )
            prog = args[0]
            return (
                f"execve(\"{prog}\", [\"{prog}\"], envp) = 0\n"
                f"brk(NULL)                               = 0x55a1234\n"
                f"openat(AT_FDCWD, \"/etc/ld.so.cache\", O_RDONLY|O_CLOEXEC) = 3\n"
                f"read(3, \"\\177ELF\", 4)                   = 4\n"
                f"close(3)                                = 0\n"
                f"+++ exited with 0 +++"
            )

        elif cmd == "ltrace":
            if not args:
                return "ltrace: missing program to trace"
            prog = args[0]
            return (
                f"__libc_start_main(0x400526, 1, 0x7fff..., ...) = 0\n"
                f"printf(\"Hello, World!\\n\")                  = 14\n"
                f"+++ exited (status 0) +++"
            )

        elif cmd == "ldd":
            if not args:
                return "ldd: missing file operand"
            filename = args[-1]
            return (
                f"\tlinux-vdso.so.1 (0x00007ffcabcde000)\n"
                f"\tlibc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f1234560000)\n"
                f"\t/lib64/ld-linux-x86-64.so.2 (0x00007f1234780000)"
            )

        elif cmd == "nm":
            if not args:
                return "nm: missing file operand"
            filename = args[-1]
            node = navigate_to(current_path)
            if filename not in node:
                return f"nm: {filename}: No such file or directory"
            return (
                f"0000000000000000 T main\n"
                f"                 U printf\n"
                f"0000000000000010 T helper_func\n"
                f"0000000000601040 D global_var"
            )

        elif cmd == "readelf":
            if not args or (len(args) == 1 and args[0].startswith("-")):
                return "readelf: warning: Nothing to do.\nUsage: readelf <option(s)> elf-file(s)"
            filename = [a for a in args if not a.startswith("-")]
            if not filename:
                return "readelf: no input file"
            filename = filename[0]
            if "-h" in args or "--file-header" in args:
                return (
                    "ELF Header:\n"
                    "  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00\n"
                    "  Class:                             ELF64\n"
                    "  Data:                              2's complement, little endian\n"
                    "  Version:                           1 (current)\n"
                    "  OS/ABI:                            UNIX - System V\n"
                    "  Type:                              EXEC (Executable file)\n"
                    "  Machine:                           Advanced Micro Devices X86-64\n"
                    "  Entry point address:               0x401050"
                )
            if "-S" in args or "--sections" in args:
                return (
                    "There are 29 section headers, starting at offset 0x3818:\n\n"
                    "Section Headers:\n"
                    "  [Nr] Name              Type             Address           Offset\n"
                    "  [ 0]                   NULL             0000000000000000  00000000\n"
                    "  [ 1] .text             PROGBITS         0000000000401050  00001050\n"
                    "  [ 2] .data             PROGBITS         0000000000403000  00003000\n"
                    "  [ 3] .bss              NOBITS           0000000000403020  00003020"
                )
            return f"[Simulated: readelf {' '.join(args)}]"

        elif cmd == "objdump":
            if not args or (len(args) == 1 and args[0].startswith("-")):
                return "objdump: no input file specified"
            filename = [a for a in args if not a.startswith("-")]
            if not filename:
                return "objdump: no input file"
            filename = filename[0]
            if "-d" in args or "--disassemble" in args:
                return (
                    f"{filename}:     file format elf64-x86-64\n\n"
                    "Disassembly of section .text:\n\n"
                    "0000000000401050 <main>:\n"
                    "  401050:\t55                   \tpush   %rbp\n"
                    "  401051:\t48 89 e5             \tmov    %rsp,%rbp\n"
                    "  401054:\tb8 00 00 00 00       \tmov    $0x0,%eax\n"
                    "  401059:\t5d                   \tpop    %rbp\n"
                    "  40105a:\tc3                   \tret"
                )
            return f"[Simulated: objdump {' '.join(args)}]"

        elif cmd == "gdb":
            if not args:
                return (
                    "GNU gdb (Ubuntu 12.1) 12.1 (simulated)\n"
                    "Type \"help\" for help.\n"
                    "(gdb) (interactive mode not supported in simulator)"
                )
            return (
                f"GNU gdb (Ubuntu 12.1) 12.1 (simulated)\n"
                f"Reading symbols from {args[0]}...\n"
                f"(gdb) (interactive mode not supported in simulator)"
            )

        elif cmd == "bc":
            if not args:
                return "bc 1.07.1 (simulated)\nCopyright 1991-1994 Free Software Foundation\n(interactive mode not supported — use: echo '2+2' | bc)"
            expr = " ".join(args)
            try:
                import ast
                expr = expr.replace("^", "**")
                tree = ast.parse(expr, mode='eval')
                for node in ast.walk(tree):
                    if not isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp,
                                             ast.Constant, ast.Add, ast.Sub, ast.Mult,
                                             ast.Div, ast.Mod, ast.Pow, ast.FloorDiv,
                                             ast.USub, ast.UAdd)):
                        return "(standard_in) 1: syntax error"
                result = eval(compile(tree, '<bc>', 'eval'))
                return str(result)
            except:
                return "(standard_in) 1: syntax error"

        elif cmd == "expr":
            if not args:
                return "expr: missing operand"
            try:
                expr = " ".join(args)
                # Handle basic arithmetic and string ops
                if "+" in args or "-" in args or "*" in args or "/" in args or "%" in args:
                    nums = []
                    op = None
                    for a in args:
                        if a in ("+", "-", "*", "/", "%"):
                            op = a
                        else:
                            try: nums.append(int(a))
                            except: return "expr: non-numeric argument"
                    if op and len(nums) >= 2:
                        ops = {"+": nums[0]+nums[1], "-": nums[0]-nums[1],
                               "*": nums[0]*nums[1], "/": nums[0]//nums[1] if nums[1] != 0 else "division by zero",
                               "%": nums[0]%nums[1] if nums[1] != 0 else "division by zero"}
                        return str(ops[op])
                if ":" in args:
                    return "0"
                return " ".join(args)
            except:
                return "expr: syntax error"

        elif cmd == "xargs":
            if not args:
                return "[xargs: reads from stdin — not supported in simulator]\nUsage: xargs [options] [command]"
            return f"[Simulated: xargs {' '.join(args)}]"

        elif cmd == "column":
            if not args:
                return "column: missing file operand"
            node = navigate_to(current_path)
            filename = [a for a in args if not a.startswith("-")]
            if not filename:
                return "column: missing file operand"
            filename = filename[0]
            if filename not in node:
                return f"column: cannot open {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return "column: Is a directory"
            return content  # simplified — just return as-is

        elif cmd == "paste":
            if len(args) < 2:
                return "paste: missing file operand"
            node = navigate_to(current_path)
            files = [a for a in args if not a.startswith("-")]
            contents = []
            for f in files:
                if f not in node:
                    return f"paste: {f}: No such file or directory"
                if isinstance(node[f], dict):
                    return f"paste: {f}: Is a directory"
                contents.append(node[f].split("\n"))
            result = []
            for row in zip(*contents):
                result.append("\t".join(row))
            return "\n".join(result)

        elif cmd == "nl":
            if not args:
                return "nl: missing file operand"
            node = navigate_to(current_path)
            filename = [a for a in args if not a.startswith("-")]
            if not filename:
                return "nl: missing file operand"
            filename = filename[0]
            if filename not in node:
                return f"nl: {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return "nl: Is a directory"
            lines = content.split("\n")
            return "\n".join(f"{i+1:6}\t{line}" for i, line in enumerate(lines))

        elif cmd == "fmt":
            if not args:
                return "fmt: missing file operand"
            node = navigate_to(current_path)
            filename = [a for a in args if not a.startswith("-")]
            if not filename:
                return "fmt: missing file operand"
            filename = filename[0]
            if filename not in node:
                return f"fmt: {filename}: No such file or directory"
            content = node[filename]
            if isinstance(content, dict):
                return "fmt: Is a directory"
            # Simple word wrap at 75 chars
            words = content.split()
            lines, line = [], ""
            for w in words:
                if len(line) + len(w) + 1 > 75:
                    lines.append(line)
                    line = w
                else:
                    line = (line + " " + w).strip()
            if line:
                lines.append(line)
            return "\n".join(lines)

        elif cmd == "exit":
            return "logout\nConnection to linux-simulator closed."

        elif cmd == "clear":
            return "__clear__"

        elif cmd == "help":
            return (
                "Supported commands:\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Navigation:    pwd  ls  cd  find  which  type  dirname  basename\n"
                "Files:         touch  mkdir  rm  cp  mv  cat  ln  stat  chmod  chown\n"
                "Text:          echo  head  tail  wc  grep  sort  uniq  cut  tr  rev  tac\n"
                "               awk  sed  printf  less  more  column  paste  nl  fmt\n"
                "Editors:       nano  vim  vi\n"
                "Archive:       tar  zip  unzip\n"
                "Binary/Data:   strings  xxd  base64  file  diff  md5sum  sha256sum\n"
                "               nm  readelf  objdump  ldd  strace  ltrace  gdb\n"
                "System:        whoami  hostname  id  uname  date  uptime  ps  kill\n"
                "               df  free  du  cal  env  export  alias  sleep  seq\n"
                "               top  htop  vmstat  iostat  dmesg  journalctl  service\n"
                "               lscpu  lsblk  lsof  jobs  bg  fg  sudo  su  watch\n"
                "               systemctl  crontab  who  w  last  nohup  at  screen  tmux\n"
                "               lspci  lsusb  lshw  fdisk  blkid  mount  umount  bc  expr\n"
                "User Mgmt:     passwd  useradd  userdel  usermod  groups  chgrp\n"
                "Network:       ping  curl  wget  ssh  netstat  ss  ifconfig  ip\n"
                "               nslookup  dig  traceroute  nc  netcat  rsync  scp\n"
                "               whois  host  mtr  arp  ufw  iptables  nmcli  iwconfig\n"
                "Package Mgmt:  apt  apt-get  pip  pip3  npm\n"
                "Dev:           git  python3  python  node  nodejs  make  gcc  g++\n"
                "Utilities:     history  man  clear  help  exit  tee  readlink  xargs  yes\n"
                "Fun:           neofetch  cowsay"
            )

        else:
            return f"{cmd}: command not found"

    except Exception as e:
        return f"Error: {str(e)}"
