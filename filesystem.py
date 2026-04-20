# filesystem.py

file_system = {
    "/": {
        "home": {
            "student": {
                "readme.txt": "Welcome to Linux Command Simulator"
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
