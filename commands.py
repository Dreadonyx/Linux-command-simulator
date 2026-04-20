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
                     "md5sum", "sha256sum", "yes", "true", "false", "type"]
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
                     "basename", "md5sum", "sha256sum", "yes", "true", "false"]
            if cmd_name in known:
                return f"{cmd_name} is /usr/bin/{cmd_name}"
            return f"bash: type: {cmd_name}: not found"

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
                "Editors:       nano\n"
                "Binary/Data:   strings  xxd  base64  file  diff  md5sum  sha256sum\n"
                "System:        whoami  hostname  id  uname  date  uptime  ps  kill\n"
                "               df  free  cal  env  export  alias  sleep  seq\n"
                "Utilities:     history  man  clear  help  exit  tee  readlink  yes\n"
                "Fun:           neofetch  cowsay"
            )

        else:
            return f"{cmd}: command not found"

    except Exception as e:
        return f"Error: {str(e)}"
