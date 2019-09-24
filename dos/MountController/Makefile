PYTHONPATH = /home/rconan/anaconda3
MODELNAME = Mount
PYVERSION = 3.7
all: 
	cython -3 $(MODELNAME).pyx -o $(MODELNAME).pyx.c 
	gcc -fPIC -I. -I$(PYTHONPATH)/include/ -I$(PYTHONPATH)/include/python$(PYVERSION)m/ -I$(PYTHONPATH)/lib/python3.7/site-packages/numpy/core/include -o $(MODELNAME).pyx.o -c $(MODELNAME).pyx.c 
	gcc -shared -fPIC $(MODELNAME).o $(MODELNAME)_data.o $(MODELNAME).pyx.o -o $(MODELNAME).so
