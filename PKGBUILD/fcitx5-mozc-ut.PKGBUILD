# Maintainer: UTUMI Hirosi <utuhiro78 at yahoo dot co dot jp>
# Contributor: Nocifer <apmichalopoulos at gmail dot com>
# Contributor: Felix Yan <felixonmars@gmail.com>
# Contributor: ponsfoot <cabezon dot hashimoto at gmail dot com>

## The UT dictionary's project page: http://linuxplayers.g1.xrea.com/mozc-ut.html

## Helpful internal stuff
_mozcver=2.30.5618.102.20241218
_pkgver=${_mozcver}

pkgname=fcitx5-mozc-ut
arch=('i686' 'x86_64')
pkgver=${_pkgver}
pkgrel=1
url='https://github.com/fcitx/mozc'
makedepends=('bazel' 'fcitx5' 'python' 'qt6-base')
source=(mozc-${_mozcver}.tar.zst
        mozcdic-ut.txt)
sha256sums=('SKIP'
            'SKIP')

prepare() {
    cd mozc-${_mozcver}/src

    # Add the UT dictionary
    cat ${srcdir}/mozcdic-ut.txt >> data/dictionary_oss/dictionary00.txt
}

build() {
    cd mozc-${_mozcver}/src
    # Fix for gcc14
    # https://github.com/fcitx/mozc/commit/6562496
    sh ../scripts/build_fcitx5_bazel
}

package() {
    pkgdesc='Mozc with Fcitx5 module'
    license=('custom')
    depends=('fcitx5')
    optdepends=('fcitx5-configtool')

    cd mozc-${_mozcver}/src
    # Install mozc-ut
    sed -i -e "s,-/usr,-${pkgdir}/usr,g" ../scripts/install_server_bazel
    sed -i -e "s,share/doc,share/licenses,g" ../scripts/install_server_bazel
    sh ../scripts/install_server_bazel
    install -Dm644 ../LICENSE ${pkgdir}/usr/share/licenses/mozc/LICENSE

    # Install fcitx5-mozc-ut
    sed -i -e "s,-/usr,-${pkgdir}/usr,g" ../scripts/install_fcitx5_bazel
    sh ../scripts/install_fcitx5_bazel
}
