export PYTHONPATH="${PYTHONPATH}:./src"
python src/test/linx_wrapper_test.py
python src/test/linx_adapter_test.py
python src/test/linx_test.py
python src/test/async_reciever_test.py
python src/test/signal_collection_test.py

pylint --output-format=parseable src/linx4py/*.py | tee pylint_out.txt
pep8 src/linx4py/*.py | tee pep8_out.txt
clonedigger --cpd-output src/linx4py/*.py -o clonedigger_out.xml
sloccount --duplicates --wide --details src/ > sloccount_out.txt
pymetrics src/linx4py/*.py > complexity.txt
pycabehtml -i complexity.txt -o complexity.html -a complexity_acc.txt -g output.png
#pyreverse -A -S -o png -p GameOfLife game_of_life/*.py

coverage run --source=src/test
coverage xml --omit="*__init__.py"

doxygen Doxyfile
