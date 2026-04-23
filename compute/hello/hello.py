from chalkcompute import Container, Image

# 1. Define an image: Python 3.12 slim + cowsay
image = Image.debian_slim("3.12").pip_install(["cowsay"])

# 2. Start a container with the "hi" volume mounted at /data
container = Container(
    image=image,
    name="hello-example",
)
container.run()

# 3. Run some commands
print("\n=== uname ===")
result = container.exec("uname", "-a")
print(result.stdout_text)

print("=== python version ===")
result = container.exec("python", "--version")
print(result.stdout_text)

print("=== cowsay ===")
result = container.exec(
    "python", "-c", "import cowsay; cowsay.cow('Hello from Chalk!')"
)
print(result.stdout_text)

# 4. Clean up
container.stop()
print("Done.")
