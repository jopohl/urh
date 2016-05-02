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
  'gnuradio-osmosdr: for more gnuradio device backends (HackRF, FunCubeDongle, RTL-SDR)'
)
source=($pkgname-$pkgver.tar.gz::https://github.com/jopohl/urh/tarball/v$pkgver)
md5sums=('81f6940b016fd953592b7e85a887b3c3')
sha256sums=('64207be2c69dd0f3d6bb3ea9b904bb0acd23e5729ed9f9a88b30941cb225b351')


build()
{
  cd "$pkgname-$pkgver"
  msg 'Building C++ Extensions...'
  python setup.py build_ext
}


package()
{
  cd "$srcdir/$pkgname-$pkgver/"

  python setup.py install --root="$pkgdir/" --optimize=1 --skip-build

  install -Dm644 urh.desktop "${pkgdir}/usr/share/applications/urh.desktop"
  install -Dm644 ./data/icons/appicon.png "${pkgdir}/usr/share/pixmaps/urh.png"

  #install -Dm644 LICENSE "$pkgdir/usr/share/licenses/${pkgname}/LICENSE"
  install -Dm644 README.md "${pkgdir}/usr/share/docs/${pkgname}/README.md"
}