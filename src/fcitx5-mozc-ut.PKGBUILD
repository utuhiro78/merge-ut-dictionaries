# Maintainer: UTUMI Hirosi <utuhiro78 at yahoo dot co dot jp>
# Contributor: Nocifer <apmichalopoulos at gmail dot com>
# Contributor: Felix Yan <felixonmars@gmail.com>
# Contributor: ponsfoot <cabezon dot hashimoto at gmail dot com>

## The UT dictionary's project page: http://linuxplayers.g1.xrea.com/mozc-ut.html

## Helpful internal stuff
_mozcver=2.28.4960.102.20230116
_pkgver=${_mozcver}

pkgname=fcitx5-mozc-ut
arch=('i686' 'x86_64')
pkgver=${_pkgver}
pkgrel=1
url='https://github.com/fcitx/mozc'
makedepends=('bazel' 'fcitx5' 'pkgconf' 'python-six' 'qt5-base')
source=(https://osdn.net/users/utuhiro/pf/utuhiro/dl/mozc-${_mozcver}.tar.bz2
        mozcdic-ut.txt)
sha256sums=('SKIP'
            'SKIP')

prepare() {
    cd mozc-${_mozcver}/src

    # Fix the Qt5 include path
    sed -i -e "s,/usr/include/x86_64-linux-gnu/qt5,/usr/include/qt,g" config.bzl

    # Fix bazel errors
    # https://github.com/google/mozc/issues/544#issuecomment-1025122998
    sed -i -e "s,android_ndk_repository,#android_ndk_repository,g" WORKSPACE.bazel

    # Add the UT dictionary
    cat ${srcdir}/mozcdic-ut.txt >> data/dictionary_oss/dictionary00.txt
}

build() {
    cd mozc-${_mozcver}/src
    env PATH="/usr/lib/jvm/java-11-openjdk/bin/:$PATH" sh ../scripts/build_fcitx5_bazel
}

package() {
    pkgdesc='Mozc module for Fcitx5 bundled with the UT dictionary'
    license=('custom')
    depends=('fcitx5')
    optdepends=('fcitx5-configtool')
    conflicts=('fcitx-mozc' 'fcitx-mozc-ut2' 'fcitx-mozc-neologd-ut' 'fcitx-mozc-neologd-ut+ut2' 'fcitx-mozc-ut-unified' 'fcitx-mozc-ut-unified-full' 'fcitx-mozc-ut' 'fcitx5-mozc' 'fcitx5-mozc-git' 'mozc-ut-common')
    provides=("fcitx5-mozc=${_mozcver}")

    cd mozc-${_mozcver}/src
    # Install mozc-ut
    # Note: sed '' doesn't expand variables. Use "".
    sed -i -e "s,-/usr,-${pkgdir}/usr,g" ../scripts/install_server_bazel
    sed -i -e "s,share/doc,share/licenses,g" ../scripts/install_server_bazel
    sh ../scripts/install_server_bazel
    install -Dm644 ../LICENSE ${pkgdir}/usr/share/licenses/mozc/ut-dictionary

    # Install fcitx5-mozc-ut
    sed -i -e "s,-/usr,-${pkgdir}/usr,g" ../scripts/install_fcitx5_bazel
    sh ../scripts/install_fcitx5_bazel
}
