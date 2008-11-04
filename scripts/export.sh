current_python_path=$PYTHONPATH
python_path=.:../share
for f in ../share/eggs/*.egg; do
    python_path=$python_path:$f
done
python_path=$python_path:$current_python_path
echo $python_path

