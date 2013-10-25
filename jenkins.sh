export PYTHONPATH = ${PYTHONPATH}:./src/linx4py
python src/test/linxAdapterTest.py
python src/test/linxTest.py

pylint --output-format=parseable src/*.py | tee pylint_out.txt
pep8 src/*.py | tee pep8_out.txt
clonedigger --cpd-output src/*.py -o clonedigger_out.xml
sloccount --duplicates --wide --details src/ > sloccount_out.txt
pymetrics src/*.py > complexity.txt
pycabehtml -i complexity.txt -o complexity.html -a complexity_acc.txt -g output.png
#pyreverse -A -S -o png -p GameOfLife game_of_life/*.py

coverage run src/test/linxAdapterTest.py
coverage run src/test/linxTest.py
coverage xml

doxygen Doxyfile
