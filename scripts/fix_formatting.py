#!/usr/bin/env python3
"""
Script pour corriger automatiquement les problèmes de formatage
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Execute a command and print the result"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - ERREUR")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - EXCEPTION: {e}")
        return False

def main():
    print("🚀 Correction automatique du formatage")
    print("=" * 50)
    
    # Aller à la racine du projet
    project_root = Path(__file__).parent.parent
    print(f"📁 Répertoire: {project_root}")
    
    # Étape 1: Corriger le formatage avec black
    success = run_command(
        "poetry run black src/ tests/ scripts/",
        "Formatage avec Black"
    )
    
    # Étape 2: Corriger les imports avec isort
    success = run_command(
        "poetry run isort src/ tests/ scripts/",
        "Tri des imports avec isort"
    ) and success
    
    # Étape 3: Vérifier avec flake8
    success = run_command(
        "poetry run flake8 src/",
        "Vérification avec flake8"
    ) and success
    
    print("=" * 50)
    if success:
        print("✅ Correction terminée avec succès!")
    else:
        print("⚠️  Quelques problèmes restent à corriger manuellement")
        print("Consultez les messages d'erreur ci-dessus")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 