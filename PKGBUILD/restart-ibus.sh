rm -rf {pkg,src}
killall mozc_server
ibus restart

printf 'export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
ibus-daemon -drx' > ~/.xprofile

#rm -rf ~/.cache/bazel/