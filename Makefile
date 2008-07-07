build:
	python setup.py build

upload:
	python setup.py build sdist bdist_egg
	rsync -r dist/ root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyJasper

publish:
	# remove development tag
	perl -npe 's/^tag_build = .dev/# tag_build = .dev/' -i setup.cfg
	svn commit
	#python setup.py build sdist bdist_egg upload
	# add development tag
	perl -npe 's/^\# tag_build = .dev/tag_build = .dev/' -i setup.cfg
	rsync -r dist/ root@cybernetics.hudora.biz:/usr/local/www/apache22/data/dist/pyJasper
	echo "now bump version number in setup.py and commit"

install: build
	sudo python setup.py install
	