install:
	python setup.py build && sudo python setup.py install

uninstall:
	sudo rm -vrf /usr/lib/python2.5/site-packages/touchwizard
	sudo rm -v /usr/lib/python2.5/site-packages/touchwizard*.egg-info
	sudo rm -vrf /usr/share/touchwizard
