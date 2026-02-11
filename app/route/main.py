import tomllib
from pathlib import Path
from fastapi import APIRouter

root_routes = APIRouter()


def load_project_metadata() -> dict:
    """
    Charge les métadonnées du projet depuis le fichier `pyproject.toml`.

    Retourne la section `[project]` du fichier TOML.
    En cas d’erreur (fichier absent, structure invalide),
    retourne un dictionnaire vide.
    """
    try:
        # Remonter à la racine du projet (ex: app/route -> racine)
        toml_path = Path(__file__).resolve().parents[2] / "pyproject.toml"

        with toml_path.open("rb") as file:
            return tomllib.load(file).get("project", {})
    except Exception:
        return {}


# Chargement unique des métadonnées au démarrage
PROJECT_METADATA = load_project_metadata()


@root_routes.get(
    "/",
    summary="Informations générales de l’API",
    description="Expose les métadonnées de l’application "
                "(nom, version, équipe).",
)
def read_root():
    """
    Endpoint racine de l’API.

    Retourne :
    - nom de l’application
    - version
    - description
    - message d’accueil
    - équipe de développement
    """
    authors = PROJECT_METADATA.get("authors", [])

    team = [
        {
            "name": author.get("name"),
            "email": author.get("email"),
            "role": "Développeur",
        }
        for author in authors
    ]

    return {
        "app_name": PROJECT_METADATA.get("name", "Unknown"),
        "version": PROJECT_METADATA.get("version", "0.0.0"),
        "description": PROJECT_METADATA.get("description"),
        "message": "Bienvenue dans l'API des transactions bancaires",
        "team": team,
    }
