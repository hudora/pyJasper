build:
	python setup.py build

upload:
	python setup.py build sdist bdist_egg
	rsync -r dist/ root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyJasper
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/nonpublic/eggs/
	
publish:
	python setup.py build sdist bdist_egg upload
	rsync -r dist/ root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyJasper
	rsync dist/* root@cybernetics.hudora.biz:/usr/local/www/apache22/data/nonpublic/eggs/

install: build
	sudo python setup.py install
	