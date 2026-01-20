from filesystem import file_system, current_path, navigate_to, get_current_dir
from datetime import datetime
import platform
import random

# Simulated command history
command_history = []

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

    try:
        if cmd == "pwd":
            return get_current_dir()

        elif cmd == "ls":
            show_long = "-l" in args or "-la" in args or "-al" in args
            show_all = "-a" in args or "-la" in args or "-al" in args
            node = navigate_to(current_path)
            items = list(node.keys())
            if show_all:
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
                     "cp", "mv", "man", "which", "exit", "neofetch", "cowsay", "cal"]
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
            cow = f"""
 {"_" * width}
< {text} >
 {"-" * width}
        \\   ^__^
         \\  (oo)\\_______
            (__)\\       )\\/\\
                ||----w |
                ||     ||"""
            return cow

        elif cmd == "exit":
            return "logout\nConnection to linux-simulator closed."

        elif cmd == "clear":
            return "__clear__"

        elif cmd == "help":
            return (
                "Supported commands:\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                "Navigation:   pwd  ls  cd  find  which\n"
                "Files:        touch  mkdir  rm  cp  mv  cat\n"
                "Text:         echo  head  tail  wc  grep\n"
                "System:       whoami  hostname  id  uname  date\n"
                "              uptime  ps  kill  df  free  cal\n"
                "Utilities:    history  man  clear  help  exit\n"
                "Fun:          neofetch  cowsay"
            )

        else:
            return f"{cmd}: command not found"

    except Exception as e:
        return f"Error: {str(e)}"
