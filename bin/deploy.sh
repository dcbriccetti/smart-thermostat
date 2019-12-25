TARGET=/Volumes/CIRCUITPY
cp -vR src/*.py src/cpx $TARGET
rm $TARGET/cpx/boot.py
cp -v src/main.py $TARGET/code.py
cp -v src/cpx/boot.py $TARGET
