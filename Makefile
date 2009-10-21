# setting the PATH seems only to work in GNUmake not in BSDmake
PATH := ./testenv/bin:$(PATH)

default: dependencies check test

hudson: clean dependencies test statistics coverage
	find ./pyjasper/backend/tests/ -name '*.py' | xargs /usr/local/hudorakit/bin/hd_pep8
	/usr/local/hudorakit/bin/hd_pylint -f parseable ./pyjasper/backend/tests/
	# we can't use tee because it eats the error code from hd_pylint
	/usr/local/hudorakit/bin/hd_pylint -f parseable ./pyjasper/backend/tests/ > .pylint.out
	printf 'YVALUE=' > .pylint.score
	grep "our code has been rated at" < .pylint.out | cut -d '/' -f 1 | cut -d ' ' -f 7 >> .pylint.score

check:
	-find ./pyjasper/backend/tests/ -name '*.py' | xargs /usr/local/hudorakit/bin/hd_pep8
	-/usr/local/hudorakit/bin/hd_pylint ./pyjasper/backend/tests/ 

# send the jrxml to the pyjasper server and check if what's returned is a PDF
test: dependencies
	#bash pyjasper/backend/tests/test.sh
	#python pyjasper/tests.py

coverage: dependencies
	PYTHONPATH=. python /usr/local/hudorakit/bin/hd_figleaf --ignore-pylibs ./pyjasper/backend/tests/test.sh
	printf '/usr/local/lib/.*\n/opt/.*\ntestenv/.*\n' > figleaf-exclude.txt
	printf '.*manage.py\n.*settings.py\n.*setup.py\n.*urls.py\n' >> figleaf-exclude.txt
	# fix pathnames 
	perl -npe "s|`pwd`/||g;" -i.bak .figleaf 
	python /usr/local/hudorakit/bin/hd_figleaf2html -d ./coverage -x figleaf-exclude.txt
	echo "Coverage: " `grep -A3 ">totals:<" coverage/index.html|tail -n1|cut -c 9-13|cut -d'<' -f1`
	test `grep -A3 ">totals:<" coverage/index.html|tail -n1|cut -c 9-13|cut -d'.' -f1` -ge 50
	printf 'YVALUE=' > .coverage.score
	grep -A3 ">totals:<" coverage/index.html|tail -n1|cut -c 9-12 >> .coverage.score

dependencies:
	virtualenv testenv
	pip -q install -E testenv -r ./pyjasper/backend/tests/requirements.txt

statistics:
	sloccount --wide --details . | grep -v -E '(testenv|build|.svn)/' | tee .sloccount.sc

build: # doc
	python setup.py build sdist

upload: build
	rsync -vpP dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/nonpublic/eggs/

install: build
	sudo python setup.py install

clean:
	rm -Rf testenv build dist html test.db pylint.out sloccount.sc pip-log.txt .coverage.score .pylint.score .figleaf
	find . -name '*.pyc' -or -name '*.pyo' -delete
	#(cd doc; make clean)

doc:
	(cd doc; make doc)

.html:
	rst2html.py < $< > html/$*.html

.PHONY: doc build clean install upload check
