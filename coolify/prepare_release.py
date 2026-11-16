"""Prépare l'archive serveur 3.0.0 pour le déploiement sur Coolify."""
import base64
import hashlib
import os
import secrets
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ARCHIVE = Path("Petit-Cocon-serveur-3.0.0.zip")
RELEASE_DIR = Path("release").resolve()
ARCHIVE_SHA256 = "7240a39acaa527bf4dfdefdef235304cc91e4d19502b9f202e5a0cba46df719f"
ASSETS_DIR = "app/src/main/assets"
ASSETS = (
    "accounts.js", "app.js", "core-v2.js", "family.js", "features-v2.js",
    "icon-192.png", "icon-512.png", "icon.svg", "index.html",
    "manifest.webmanifest", "model.js", "platform.js", "style.css",
    "sw.js", "who-data.js",
)
FILES = (
    "server/accounts.py", "server/requirements.txt", "server/server.py",
    *(f"{ASSETS_DIR}/{asset}" for asset in ASSETS),
)
EDITS = (
    ("server/accounts.py", "        box = None\n        if mode in (\"create\", \"claim\"):", "        if mode == \"claim\":", 1),
    ("server/accounts.py", "            if mode == \"create\":\n                box = self.validate_box(body[\"box\"])", "        box = self.validate_box(body[\"box\"]) if mode == \"create\" else None", 1),
    ("app/src/main/assets/accounts.js", "{mode: 'create', setupKey, box:", "{mode: 'create', box:", 1),
    ("app/src/main/assets/family.js", "const setup = joining ? '' : field(", "const setup = !legacy ? '' : field(", 1),
    ("app/src/main/assets/family.js", "'Créer le premier compte'", "'Créer mon compte'", 2),
    ("app/src/main/assets/sw.js", "'petit-cocon-v3'", "'petit-cocon-v3-inscription'", 1),
)


def prepare_release():
    with ARCHIVE.open("rb") as archive_stream:
        checksum = hashlib.file_digest(archive_stream, "sha256").hexdigest()
    if checksum != ARCHIVE_SHA256:
        raise SystemExit("Utilise l’archive serveur officielle Petit-Cocon-serveur-3.0.0.zip.")

    with ZipFile(ARCHIVE) as archive:
        for name in FILES:
            path = RELEASE_DIR / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.read(name))

    for name, old, new, expected in EDITS:
        path = RELEASE_DIR / name
        source = path.read_text(encoding="utf-8")
        if source.count(old) != expected:
            raise SystemExit(f"La version du fichier {name} est incompatible avec ce build.")
        path.write_text(source.replace(old, new), encoding="utf-8")


def check_registration():
    # Deux carnets fictifs dans une base temporaire pour tester l'inscription sans clé.
    with TemporaryDirectory() as folder:
        os.environ["COCON_DATA"] = folder
        os.environ.pop("COCON_CREATE_KEY", None)
        sys.path.insert(0, str(RELEASE_DIR / "server"))
        import server

        server.init_db()
        body = {
            "mode": "create",
            "name": "Compte de test",
            "proof": secrets.token_urlsafe(32),
            "envelope": {
                "iv": base64.b64encode(bytes(12)).decode("ascii"),
                "ciphertext": base64.b64encode(bytes(48)).decode("ascii"),
            },
            "box": {"iv": "test", "ciphertext": "test"},
        }
        first = server.ACCOUNTS.register({**body, "email": "a@example.test"})
        second = server.ACCOUNTS.register({**body, "email": "b@example.test"})
        if first["family"] == second["family"] or first["account"]["role"] != "owner":
            raise SystemExit("L'inscription doit créer un carnet distinct par famille.")

        # L'ancienne migration protège toujours l'attribution du rôle de propriétaire.
        try:
            server.ACCOUNTS.register({**body, "mode": "claim", "email": "legacy@example.test"})
        except server.accounts.RequestError as error:
            if error.code != "creation_key_required":
                raise
        else:
            raise SystemExit("La migration V2 doit vérifier les accès existants.")


if __name__ == "__main__":
    prepare_release()
    check_registration()
