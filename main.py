from pathlib import Path

from src.core.app.bootstrap import Bootstrap


def BootstrapMain() -> None:
    projectRoot = Path(__file__).parent
    Bootstrap(projectRoot)


if __name__ == "__main__":
    BootstrapMain()
