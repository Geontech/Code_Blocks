AC_INIT(simple_tcp, 1.0.0)
AM_INIT_AUTOMAKE(nostdinc)

AC_PROG_INSTALL

AC_CORBA_ORB
OSSIE_CHECK_OSSIE
OSSIE_SDRROOT_AS_PREFIX
AM_PATH_PYTHON([2.4])

PKG_CHECK_MODULES([OSSIE], [ossie >= 1.9])
AC_CHECK_PYMODULE(ossie, [], [AC_MSG_ERROR([the python ossie module is required])])
PKG_CHECK_MODULES([OMNIORB], [omniORB4 >= 4.1.0])
AC_CHECK_PYMODULE(omniORB, [], [AC_MSG_ERROR([the python omniORB module is required])])

PKG_CHECK_MODULES(bulkioInterfaces, bulkioInterfaces >= 1.8) 
AC_CHECK_PYMODULE(bulkio.bulkioInterfaces, [], [AC_MSG_ERROR([the python bulkio.bulkioInterfaces module is required])])
PKG_CHECK_MODULES(frontendInterfaces, frontendInterfaces) 
AC_CHECK_PYMODULE(redhawk.frontendInterfaces, [], [AC_MSG_ERROR([the python redhawk.frontendInterfaces module is required])])

AC_CONFIG_FILES(Makefile)

AC_OUTPUT
