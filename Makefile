NOWEBPATH	= /usr/local/Cellar/noweb/2.11b
WEAVE   	= $(NOWEBPATH)/bin/noweave
TANGLE    	= $(NOWEBPATH)/bin/notangle

all: server client doc
server: simceo.nw simceo.py
	mkdir -p calibration_dbs
client:
	mkdir -p etc
	mkdir -p dos
	$(TANGLE) -Rdos.yaml simceo.nw > etc/dos.yaml
	$(TANGLE) -Rinit.py simceo.nw > dos/__init__.py
	$(TANGLE) -Rdos.py simceo.nw > dos/dos.py
	$(TANGLE) -Rdriver.py simceo.nw > dos/driver.py
	$(TANGLE) -Rcontrol.py simceo.nw > dos/control.py
service:
	$(TANGLE) -Rsimceo simceo.nw > simceo
	echo "The simceo script resides in your home ~/bin directory"
	$(TANGLE) -Rsimceo.service simceo.nw > simceo.service
	echo "The simceo script resides in /etc/systemd/system"

doc: simceo.nw simceo.tex
	make -C doc/ all

ipython:
	env LD_LIBRARY_PATH=/usr/local/cuda/lib64 PYTHONPATH=/home/ubuntu/CEO/python ipython

.SUFFIXES: .nw .tex .py .m

.nw.tex:
	$(WEAVE) -delay -index $< > doc/$@

.nw.py:
	$(TANGLE) -R$@ $< > $@

.nw.m:
	$(TANGLE) -R$@ $< > $@

