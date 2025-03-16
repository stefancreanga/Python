# Small Python and Docker project application.
# It's an SQLAlchemy very simple database with
# input validation check using Marshmallow and
# request limit using flask-limiter

# This is the Docker part. This program manages
# containers. It creates, runs, stops, removes
# and lists containers.

import docker

# Initialize Docker client
client = docker.from_env()

def list_images():
    """ List available Docker images. """
    images = client.images.list()
    if not images:
        print("No images found.")
        return None
    
    print("\nAvailable Images:")
    image_tags = []
    for idx, image in enumerate(images, start=1):
        tag = image.tags[0] if image.tags else "<none>:<none>"
        image_tags.append(tag)
        print(f"{idx}. {tag}")
    
    return image_tags

def list_containers():
    """ List all available containers (running and stopped). """
    containers = client.containers.list(all=True)
    if not containers:
        print("No containers found.")
        return None
    
    print("\nAvailable Containers:")
    for idx, container in enumerate(containers, start=1):
        print(f"{idx}. {container.name} ({container.status})")
    
    return containers

def create_and_run_container():
    """ Create and run a new container with a user-defined name. """
    image_name = input("Enter the Docker image name (default: flask_app): ") or "flask_app"
    container_name = input("Enter a name for the new container: ")

    print("Checking for existing container with the same name...")
    try:
        existing_container = client.containers.get(container_name)
        print(f"Container '{container_name}' already exists. Stopping and removing it first...")
        existing_container.stop()
        existing_container.remove()
    except docker.errors.NotFound:
        print("No existing container found. Creating a new one.")

    print(f"Running new container '{container_name}' from image '{image_name}'...")
    container = client.containers.run(image_name, name=container_name, detach=True, ports={"5000/tcp": 5000})
    print(f"Container '{container_name}' is running at http://localhost:5000")

def create_and_run_container2():
    """ Create and run a new container by selecting an image from the list. """
    image_tags = list_images()
    if not image_tags:
        return
    
    try:
        choice = int(input("Enter the number of the image to use: ")) - 1
        if 0 <= choice < len(image_tags):
            image_name = image_tags[choice]
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    container_name = input("Enter a name for the new container: ")

    print("Checking for existing container with the same name...")
    try:
        existing_container = client.containers.get(container_name)
        print(f"Container '{container_name}' already exists. Stopping and removing it first...")
        existing_container.stop()
        existing_container.remove()
    except docker.errors.NotFound:
        print("No existing container found. Creating a new one.")

    print(f"Running new container '{container_name}' from image '{image_name}'...")
    container = client.containers.run(image_name, name=container_name, detach=True, ports={"5000/tcp": 5000})
    print(f"Container '{container_name}' is running at http://localhost:5000")

def pick_and_run_container():
    """ Show a list of containers and let the user choose one to start. """
    containers = list_containers()
    if not containers:
        return
    
    choice = int(input("Enter the number of the container to start: ")) - 1
    if 0 <= choice < len(containers):
        container = containers[choice]
        container.start()
        print(f"Container '{container.name}' started.")
    else:
        print("Invalid selection.")

def stop_container():
    """ Show a list of containers and let the user choose one to stop. """
    containers = list_containers()
    if not containers:
        return
    
    choice = int(input("Enter the number of the container to stop: ")) - 1
    if 0 <= choice < len(containers):
        container = containers[choice]
        container.stop()
        print(f"Container '{container.name}' stopped.")
    else:
        print("Invalid selection.")

def remove_container():
    """ Show a list of containers and let the user choose one to remove. """
    containers = list_containers()
    if not containers:
        return
    
    choice = int(input("Enter the number of the container to remove: ")) - 1
    if 0 <= choice < len(containers):
        container = containers[choice]
        container.remove()
        print(f"Container '{container.name}' removed.")
    else:
        print("Invalid selection.")

if __name__ == "__main__":
    while True:
        print("\nDocker Management Menu:")
        print("1. Create & Run a New Container")
        print("2. Pick & Run an Existing Container")
        print("3. Stop a Running Container")
        print("4. Remove a Container")
        print("5. List containers")
        print("6. Exit")

        choice = input("Choose an option: ")
        
        if choice == "1":
            create_and_run_container2()
        elif choice == "2":
            pick_and_run_container()
        elif choice == "3":
            stop_container()
        elif choice == "4":
            remove_container()
        elif choice == "5":
            list_containers()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid option, please try again.")
