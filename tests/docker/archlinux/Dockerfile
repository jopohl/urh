FROM  base/archlinux

RUN mkdir -p /root/.gnupg\
 && pacman -Sy --noconfirm archlinux-keyring\
 && pacman -Syu --noconfirm\
 && pacman-db-upgrade\
 && pacman -S --noconfirm ca-certificates ca-certificates-mozilla\
 && pacman -S --noconfirm curl base-devel nano vim\
 && useradd -m -G wheel -s /bin/bash dockeruser\
 && echo "dockeruser ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers


WORKDIR /tmp
RUN curl -O https://aur.archlinux.org/cgit/aur.git/snapshot/package-query.tar.gz\
 && sudo -u dockeruser tar -xvzf package-query.tar.gz

WORKDIR /tmp/package-query
RUN sudo -u dockeruser makepkg -si --noconfirm

WORKDIR /tmp
RUN curl -O https://aur.archlinux.org/cgit/aur.git/snapshot/yaourt.tar.gz\
 && sudo -u dockeruser tar -xvzf yaourt.tar.gz

WORKDIR /tmp/yaourt
RUN sudo -u dockeruser makepkg -si --noconfirm

ADD install_from_aur.sh /bin/install_from_aur.sh
RUN chmod +x /bin/install_from_aur.sh
CMD /bin/install_from_aur.sh