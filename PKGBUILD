# Maintainer: Johannes Pohl <johannes.pohl90@gmail.com>
pkgname=urh
pkgver=0.9.5
pkgrel=1
pkgdesc="Universal Radio Hacker - Wireless Hacking made easy"
arch=('i686' 'x86_64')
url="https://github.com/jopohl/urh"
depends=('python>=3.4' 'python-pyqt5' 'python-numpy')
makedepends=('gcc')
optdepends=(
  'hackrf: for native hackrf backend'
  'gnuradio: for USRP gnuradio backend'
  'gnuradio-osmosdr: for more gnuradio device backends (HackRF, FunCubeDongle, RTL-SDR'
)
source=(https://github.com/jopohl/urh/tarball/v$pkgver)
md5sums=('07d90809e81e269412e5ab6080f76fe5')
sha256sums=('a83cc8c80ad91617326e5062c62a17c352c7ff05b770b34c03bd2b49a2b9e15a')

build() {
  cd "$srcdir"
  mkdir -p $pkgname-$pkgver
  tar xf v$pkgver --directory $pkgname-$pkgver --strip 1
  cd "$srcdir/$pkgname-$pkgver/"
  python setup.py build_ext
}

package() {
  cd "$srcdir/$pkgname-$pkgver/"

  # Desktop file
  install -Dm644 urh.desktop "$pkgdir/usr/share/applications/urh.desktop"

  python setup.py install

  install -Dm644 ./data/icons/appicon.png "$pkgdir/usr/share/pixmaps/urh.png"
  #install -Dm644 LICENSE "$pkgdir/usr/share/licenses/${pkgname}/LICENSE"
  install -Dm644 README.md "$pkgdir/usr/share/docs/${pkgname}/README.md"
}