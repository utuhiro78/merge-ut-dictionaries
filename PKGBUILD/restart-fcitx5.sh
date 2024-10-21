rm -rf {pkg,src}
killall fcitx5 mozc_server
fcitx5 &

printf 'export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS=@im=fcitx' > ~/.xprofile

#rm -rf ~/.cache/bazel/