# Maintainer: UTUMI Hirosi <utuhiro78 at yahoo dot co dot jp>
# Contributor: Nocifer <apmichalopoulos at gmail dot com>
# Contributor: Felix Yan <felixonmars@gmail.com>
# Contributor: ponsfoot <cabezon dot hashimoto at gmail dot com>

## The UT dictionary's project page: http://linuxplayers.g1.xrea.com/mozc-ut.html

## Helpful internal stuff
_mozcver=2.28.4990.102.20230123
_pkgver=${_mozcver}

pkgname=ibus-mozc-ut
arch=('i686' 'x86_64')
pkgver=${_pkgver}
pkgrel=1
url='https://github.com/google/mozc'
makedepends=('bazel' 'ibus' 'python' 'qt5-base')
source=(mozc-${_mozcver}.tar.bz2
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
    bazel build package --config oss_linux -c opt
}

package() {
    pkgdesc='Mozc with iBus module'
    license=('custom')
    depends=('ibus')

    cd mozc-${_mozcver}/src/
    install -Dm644 ../LICENSE ${pkgdir}/usr/share/licenses/mozc/LICENSE

    cd bazel-bin/unix/
    unzip -q mozc.zip
    rm -rf {usr/bin/,usr/share/emacs/}

    chmod 755 {usr/lib/ibus-mozc/*,usr/lib/mozc/*}
    chmod 644 {usr/share/ibus/component/*.xml,usr/share/ibus-mozc/*.png,usr/share/icons/mozc/*.*,usr/share/icons/mozc/*/*.svg}

    cp -r usr/ ${pkgdir}/
}
