#!/usr/bin/env python3

from core.cli.menu import main_menu

def main():
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[!] Interrumpido por el usuario")
    except Exception as e:
        print(f"\n[!] Error fatal: {e}")

if __name__ == "__main__":
    main()
