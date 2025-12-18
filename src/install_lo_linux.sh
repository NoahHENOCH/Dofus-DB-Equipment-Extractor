#!/bin/bash

# On arrête le script dès qu'une erreur survient (sécurité)
set -e

echo "--- Détection du système d'exploitation ---"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Impossible de détecter l'OS. Arrêt."
    exit 1
fi

echo "Système détecté : $OS"

case $OS in
    ubuntu|debian|pop|mint)
        echo "--- Préparation pour Debian/Ubuntu ---"
        
        echo "1. Mise à jour des listes de paquets..."
        apt-get update

        echo "2. Installation de l'outil de gestion intelligente 'aptitude'..."
        # On utilise apt-get ici juste pour installer aptitude si absent
        apt-get install -y aptitude

        echo "3. Mise à jour complète du système (Full Upgrade)..."
        # full-upgrade gère mieux les changements de dépendances que upgrade simple
        aptitude full-upgrade -y

        echo "4. Installation des dépendances avec Aptitude..."
        # Aptitude est meilleur pour résoudre les conflits (ex: libgtk-3, qt5)
        # L'option -y accepte la solution proposée par défaut.
        aptitude install -y \
            git build-essential zip ccache junit4 libkrb5-dev nasm \
            graphviz python3 python3-dev python3-setuptools qtbase5-dev \
            libkf5coreaddons-dev libkf5i18n-dev libkf5config-dev \
            libkf5windowsystem-dev libkf5kio-dev libqt5x11extras5-dev \
            autoconf libcups2-dev libfontconfig1-dev gperf openjdk-17-jdk \
            doxygen libxslt1-dev xsltproc libxml2-utils libxrandr-dev \
            libx11-dev bison flex libgtk-3-dev libgstreamer-plugins-base1.0-dev \
            libgstreamer1.0-dev ant ant-optional libnss3-dev libavahi-client-dev \
            libxt-dev meson gcc-12 g++-12

        echo "5. Configuration de GCC 12..."
        update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 60 --slave /usr/bin/g++ g++ /usr/bin/g++-12
        ;;

    fedora|rhel|centos)
        echo "Installation des dépendances pour Fedora/RHEL..."
        dnf builddep -y libreoffice
        dnf install -y meson
        ;;

    arch|manjaro)
        echo "Installation des dépendances pour Arch Linux..."
        pacman -S --needed --noconfirm base-devel git ccache ant apr beanshell \
        bluez-libs clucene coin-or-mp cppunit curl dbus-glib desktop-file-utils \
        doxygen flex gcc-libs gdb glm gobject-introspection gperf gpgme graphite \
        gst-plugins-base-libs gtk3 harfbuzz-icu hicolor-icon-theme hunspell hyphen \
        icu jdk17-openjdk junit lcms2 libabw libatomic_ops libcdr libcmis libe-book \
        libepoxy libepubgen libetonyek libexttextcat libfreehand libgl libjpeg \
        liblangtag libmspub libmwaw libmythes libnumbertext libodfgen liborcus \
        libpagemaker libqxp libstaroffice libtommath libvisio libwpd libwpg libwps \
        libxinerama libxrandr libxslt libzmf lpsolve mariadb-libs mdds nasm neon \
        nspr nss pango poppler postgresql-libs python qt5-base redland sane serf \
        sh shared-mime-info ttf-liberation unixodbc unzip xmlsec zip gtk4 qt6-base \
        zxing-cpp abseil-cpp meson
        ;;

    suse*|opensuse*)
        echo "Installation des dépendances pour openSUSE..."
        zypper in -y git autoconf automake bison make gcc gcc-c++ cups-devel \
        fontconfig-devel gperf java-17-openjdk-devel libxslt-devel python3-devel \
        krb5-devel libX11-devel libXext-devel libICE-devel libSM-devel libXt-devel \
        libXrender-devel libXrandr-devel flex gtk3-devel gstreamer-devel \
        gstreamer-plugins-base-devel ant junit nasm ccache binutils-gold mozilla-nss-devel meson
        ;;

    *)
        echo "Distribution non supportée par ce script automatique."
        exit 1
        ;;
esac

echo "--- Préparation du dépôt Git ---"
if [ ! -d "libreoffice" ]; then
    # Clone initial
    git clone https://gerrit.libreoffice.org/core libreoffice
fi
cd libreoffice

echo "--- Configuration du Build (autogen) ---"

cat <<EOF > autogen.input
--enable-dbgutil
--without-doxygen
--without-java
EOF

./autogen.sh

echo "--- Lancement de la compilation (Build) ---"
echo "Attention : cela peut prendre plusieurs heures."
# Utilisation de make check pour valider le build
# make

exit 0
