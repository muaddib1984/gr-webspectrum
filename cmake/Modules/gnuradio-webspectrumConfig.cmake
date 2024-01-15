find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_WEBSPECTRUM gnuradio-webspectrum)

FIND_PATH(
    GR_WEBSPECTRUM_INCLUDE_DIRS
    NAMES gnuradio/webspectrum/api.h
    HINTS $ENV{WEBSPECTRUM_DIR}/include
        ${PC_WEBSPECTRUM_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_WEBSPECTRUM_LIBRARIES
    NAMES gnuradio-webspectrum
    HINTS $ENV{WEBSPECTRUM_DIR}/lib
        ${PC_WEBSPECTRUM_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-webspectrumTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_WEBSPECTRUM DEFAULT_MSG GR_WEBSPECTRUM_LIBRARIES GR_WEBSPECTRUM_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_WEBSPECTRUM_LIBRARIES GR_WEBSPECTRUM_INCLUDE_DIRS)
