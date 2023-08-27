import os 

def main():
    for dirname, dirs, files in os.walk('wheels'):
        with open('wheels.txt', 'w') as f:
            f.write("\n".join(files))


if __name__ == "__main__":
    main()