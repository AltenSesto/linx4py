export PYTHONPATH="${PYTHONPATH}:./src"
python src/test/linxAdapterTest.py
python src/test/linxTest.py
python src/test/asyncRecieverTest.py
python src/test/signalCollectionTest.py

pylint --output-format=parseable src/linx4py/*.py | tee pylint_out.txt
pep8 src/*.py | tee pep8_out.txt
clonedigger --cpd-output src/linx4py/*.py -o clonedigger_out.xml
sloccount --duplicates --wide --details src/ > sloccount_out.txt
pymetrics src/*.py > complexity.txt
pycabehtml -i complexity.txt -o complexity.html -a complexity_acc.txt -g output.png
#pyreverse -A -S -o png -p GameOfLife game_of_life/*.py

coverage run src/test/linxAdapterTest.py
coverage run src/test/linxTest.py
coverage run src/test/asyncRecieverTest.py
coverage run src/test/signalCollectionTest.py
coverage xml

doxygen Doxyfile
