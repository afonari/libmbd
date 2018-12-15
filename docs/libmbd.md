---
project: Libmbd
summary: Many-body dispersion library
license: by
src_dir: ../src
output_dir: build/fortran
css: tweaks.css
preprocessor: gfortran -cpp -E -P -DWITH_MPI -DWITH_SCALAPACK
exclude:
    mbd_blacs.f90
    mbd_coulomb.f90
    mbd_density.f90
    mbd_lapack.f90
    mbd_linalg.F90
    mbd_matrix.F90
    mbd_mpi.F90
    mbd_rpa.F90
    mbd_scalapack.f90
    mbd_utils.F90
---