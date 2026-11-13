#!/usr/bin/env python3

"""
🤖 GITHUB AGENT - COLLECTOR
---------------------------
Ce script est un agent autonome qui :
1. Vous demande vos accès et ce que vous cherchez.
2. Scanne GitHub via l'API.
3. Télécharge (clone) les projets en parallèle.
4. Nettoie les fichiers (.git).
5. Vous donne un fichier ZIP final.
"""

import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

# Tentative d'import des librairies externes
try:
    import requests
    from tqdm import tqdm
except ImportError:
    print("❌ Erreur : Il manque des librairies.")
    print("Veuillez lancer : pip install requests tqdm")
    sys.exit(1)

# =====================================================
# Configuration
# =====================================================

BASE_DIR = Path.cwd() / "github_agent_downloads"
WORK_DIR = BASE_DIR / "temp_repos"

# =====================================================
# Fonctions Utilitaires
# =====================================================


def clean_filename(text):
    """Nettoie le nom des dossiers pour éviter les erreurs Windows/Linux."""
    # Garde seulement alphanumérique, tirets et underscores
    return re.sub(r"[^\w\-_]", "_", text)


def print_banner():
    print("\n" + "=" * 60)
    print("      🤖 GITHUB AUTO-COLLECTOR AGENT")
    print("      Recherche -> Clone -> Zip")
    print("=" * 60 + "\n")


def check_git_installed():
    try:
        subprocess.run(
            ["git", "--version"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False


# =====================================================
# 1. Module de Recherche (API GitHub)
# =====================================================


def search_github(query, limit, token):
    print(f"\n🔎 Recherche des {limit} meilleurs dépôts pour : '{query}'...")

    api_url = "https://api.github.com/search/repositories"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "Github-Agent-v2"}
    if token:
        headers["Authorization"] = f"token {token}"

    repos_found = []
    page = 1
    per_page = 100  # Max autorisé par GitHub par page

    while len(repos_found) < limit:
        params = {
            "q": query,
            "sort": "stars",  # On veut les plus populaires
            "order": "desc",
            "per_page": per_page,
            "page": page,
        }

        try:
            r = requests.get(api_url, headers=headers, params=params, timeout=10)

            if r.status_code == 401:
                print("❌ Erreur : Votre Token est invalide.")
                return []
            elif r.status_code == 403:
                print("⚠️ Limite d'API GitHub atteinte (Rate Limit).")
                break
            elif r.status_code != 200:
                print(f"⚠️ Erreur API ({r.status_code})")
                break

            data = r.json()
            items = data.get("items", [])

            if not items:
                break  # Plus de résultats

            for item in items:
                repos_found.append(
                    {
                        "name": item["name"],
                        "full_name": item["full_name"],
                        "clone_url": item["clone_url"],
                        "stars": item["stargazers_count"],
                        "owner": item["owner"]["login"],
                    }
                )
                if len(repos_found) >= limit:
                    break

            page += 1
            if page > 10:
                break  # Sécurité anti-boucle infinie

        except requests.RequestException as e:
            print(f"❌ Erreur de connexion : {e}")
            break

    # On trie une dernière fois par étoiles au cas où
    repos_found.sort(key=lambda x: x["stars"], reverse=True)
    return repos_found[:limit]


# =====================================================
# 2. Module de Clonage
# =====================================================


def clone_single_repo(repo_info, token):
    """Fonction exécutée par les threads pour cloner."""
    # Nom du dossier : NomRepo_Proprietaire (pour éviter les doublons)
    folder_name = clean_filename(f"{repo_info['name']}_{repo_info['owner']}")
    target_path = WORK_DIR / folder_name

    if target_path.exists():
        return None  # Déjà cloné

    # URL authentifiée pour éviter les limites de clonage
    clone_url = repo_info["clone_url"]
    if token and clone_url.startswith("https://github.com/"):
        auth_url = clone_url.replace("https://", f"https://{token}@", 1)
    else:
        auth_url = clone_url

    # Variables d'environnement pour empêcher Git de demander un mot de passe (bloquant)
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", auth_url, str(target_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=180,  # 3 minutes max par repo
            check=True,
            env=env,
        )

        # Nettoyage : on supprime le dossier caché .git pour alléger le ZIP
        git_hidden = target_path / ".git"
        if git_hidden.exists():
            shutil.rmtree(git_hidden, ignore_errors=True)

        return repo_info
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        # Si échec, on nettoie le dossier vide
        if target_path.exists():
            shutil.rmtree(target_path, ignore_errors=True)
        return None


# =====================================================
# MAIN LOOP
# =====================================================


def main():
    print_banner()

    # 0. Vérification Git
    if not check_git_installed():
        print("❌ Erreur : GIT n'est pas installé sur cet ordinateur.")
        print("Installez Git ici : https://git-scm.com/downloads")
        sys.exit(1)

    # 1. Inputs Utilisateur (INTERACTIF)
    print("📝 VEUILLEZ RÉPONDRE AUX QUESTIONS :\n")

    # A. Token
    print("1. Collez votre Token GitHub (Classic) pour l'accès API.")
    print(
        "   (Si vous n'en avez pas, appuyez juste sur Entrée, mais la recherche sera limitée)"
    )
    user_token = input("   👉 Token : ").strip()

    # B. Recherche
    print(
        "\n2. Que cherchez-vous ? (ex: 'trading bot python', 'portfolio react', 'django ecommerce')"
    )
    user_query = input("   👉 Recherche : ").strip()
    if not user_query:
        print("❌ Vous devez écrire quelque chose !")
        sys.exit(1)

    # C. Nombre
    print("\n3. Combien de projets voulez-vous télécharger ? (ex: 10, 50, 100)")
    try:
        count_str = input("   👉 Nombre : ").strip()
        user_limit = int(count_str)
    except ValueError:
        user_limit = 10  # Défaut
        print("⚠️ Nombre invalide, on part sur 10 par défaut.")

    # 2. Préparation Dossiers
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR, ignore_errors=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # 3. Lancement Recherche
    repos = search_github(user_query, user_limit, user_token)

    if not repos:
        print("\n❌ Aucun dépôt trouvé. Fin du programme.")
        sys.exit(0)

    print(f"\n✅ {len(repos)} projets identifiés. Démarrage du téléchargement...")

    # 4. Clonage Multi-thread
    success_count = 0

    # On utilise 8 "ouvriers" en parallèle pour aller vite
    with ThreadPoolExecutor(max_workers=8) as executor:
        # On prépare les tâches
        futures = [executor.submit(clone_single_repo, r, user_token) for r in repos]

        # On affiche la barre de progression
        for future in tqdm(
            futures, total=len(repos), desc="⬇️  Téléchargement", unit="repo"
        ):
            result = future.result()
            if result:
                success_count += 1

    # 5. Rapport
    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mm")
    report_file = WORK_DIR / "_RAPPORT_DE_RECHERCHE.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"Rapport généré le {timestamp}\n")
        f.write(f"Recherche : {user_query}\n")
        f.write(f"Projets demandés : {user_limit}\n")
        f.write(f"Projets téléchargés : {success_count}\n")
        f.write("-" * 30 + "\n")
        f.writelines(
            f"[{r['stars']}★] {r['full_name']} -> {r['clone_url']}\n" for r in repos
        )

    # 6. Compression (ZIP)
    print("\n📦 Création de l'archive ZIP...")
    safe_query_name = clean_filename(user_query)
    zip_filename = f"GITHUB_{safe_query_name}_{timestamp}"
    output_zip_path = BASE_DIR / zip_filename

    shutil.make_archive(str(output_zip_path), "zip", WORK_DIR)

    # Nettoyage temporaire
    shutil.rmtree(WORK_DIR, ignore_errors=True)

    print("\n" + "=" * 60)
    print("✅ MISSION ACCOMPLIE !")
    print("📂 Votre fichier est prêt ici :")
    print(f"   👉 {output_zip_path}.zip")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt forcé par l'utilisateur.")
    except Exception as e:  # noqa: BLE001 - last-resort message for the interactive CLI
        print(f"\n❌ Erreur inattendue : {e}")
