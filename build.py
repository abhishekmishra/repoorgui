import argparse
import sys
import PyInstaller.__main__

if __name__ == "__main__":
    parser = argparse.ArgumentParser("repoorgui builder arguments")
    parser.add_argument('command')
    args = parser.parse_args()
    if args.command == "installer":
        print('creating installer')
        PyInstaller.__main__.run([
            'repoorgui.py',
            '--onefile',
            '--windowed'
        ])
    else:
        print('Error: command not recognized ->',
              args.command, '!', file=sys.stderr)
