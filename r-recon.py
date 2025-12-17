#!/usr/bin/env python3

from core.banner import show_banner
from core.menu import main_menu

def main():
    try:
        show_banner()
        main_menu()
    except KeyboardInterrupt:
        print("\n\n[!] Programa interrumpido por el usuario")
        exit(0)
    except Exception as e:
        print(f"\n[!] Error inesperado: {e}")
        exit(1)

if __name__ == "__main__":
    main()