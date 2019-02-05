LOCALBASE?=	/usr/local
PREFIX?=	${LOCALBASE}

# Where to install the helper python scripts
PYTHONDIR=	${PREFIX}/share/libcxx-gdbpy/python
DATADIR=	${PYTHONDIR}/libcxx

# Where to install the GDB auto-load script.  LIBCXX_DIR is the
# directory containing the libc++ shared library.  LIBCXX is the
# filename of the shared library.
AUTO_LOAD_DIR=	${PREFIX}/share/gdb/auto-load
LIBCXX_DIR=	/usr/lib
LIBCXX=		libc++.so.1

install:
	install -d ${DESTDIR}${DATADIR}
	install -m 644 python/libcxx/__init__.py ${DESTDIR}${DATADIR}
	install -m 644 python/libcxx/printers.py ${DESTDIR}${DATADIR}
	install -m 644 python/libcxx/xmethods.py ${DESTDIR}${DATADIR}
	install -d ${DESTDIR}${AUTO_LOAD_DIR}${LIBCXX_DIR}
	sed -e "s,PYTHONDIR,${PYTHONDIR}," python/libc++-gdb.py > \
	    ${DESTDIR}${AUTO_LOAD_DIR}${LIBCXX_DIR}/${LIBCXX}-gdb.py

