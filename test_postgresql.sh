#!/bin/bash

echo "🐘 Installation de PostgreSQL pour test local"

# Windows (avec Chocolatey)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "Installation sur Windows..."
    choco install postgresql
    
# macOS
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installation sur macOS..."
    brew install postgresql
    brew services start postgresql
    
# Linux (Ubuntu/Debian)
else
    echo "Installation sur Linux..."
    sudo apt update
    sudo apt install postgresql postgresql-contrib -y
    sudo systemctl start postgresql
fi

echo "✅ PostgreSQL installé!"
echo ""
echo "📝 Créer la base de données de test :"
echo "   sudo -u postgres createdb bibliotech_test"
echo ""
echo "🔧 Modifier votre .env :"
echo "   DATABASE_URL=postgresql://postgres:password@localhost/bibliotech_test"