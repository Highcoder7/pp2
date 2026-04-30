def total(*args):
    return sum(args)

def show_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

def mixed(title, *args, **kwargs):
    print(f"Title: {title}")
    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")

print(total(1, 2, 3, 4, 5))
show_info(name="Esen", age=21, city="Astana")
mixed("Demo", 10, 20, color="blue", size="large")
