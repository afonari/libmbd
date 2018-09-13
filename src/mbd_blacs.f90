! This Source Code Form is subject to the terms of the Mozilla Public
! License, v. 2.0. If a copy of the MPL was not distributed with this
! file, You can obtain one at http://mozilla.org/MPL/2.0/.
module mbd_blacs

use mbd_constants

implicit none

private
public :: mbd_blacs_desc, mbd_blacs_grid, all_reduce

type :: mbd_blacs_grid
    integer :: ctx = -1
    integer :: nprows
    integer :: npcols
    integer :: my_prow
    integer :: my_pcol
contains
    procedure :: init => mbd_blacs_grid_init
    procedure :: destroy => mbd_blacs_grid_destroy
end type

type :: mbd_blacs_desc
    integer, allocatable :: i_atom(:)
    integer, allocatable :: j_atom(:)
    integer :: n_atoms
    integer :: desc(9)
    integer :: ctx = -1
contains
    procedure :: init => mbd_blacs_desc_init
end type

interface all_reduce
    module procedure all_reduce_real_1d
    module procedure all_reduce_real_2d
    module procedure all_reduce_complex_1d
    module procedure all_reduce_complex_2d
end interface

external :: BLACS_PINFO, BLACS_GRIDINIT, BLACS_GRIDINFO, &
    BLACS_GRIDEXIT, NUMROC, DESCINIT, DGSUM2D, ZGSUM2D, BLACS_GET
integer :: NUMROC

contains

subroutine mbd_blacs_grid_init(this, comm)
    class(mbd_blacs_grid), intent(inout) :: this
    integer, intent(in), optional :: comm

    integer :: my_task, n_tasks, nprows

    call BLACS_PINFO(my_task, n_tasks)
    do nprows = int(sqrt(dble(n_tasks))), 1, -1
        if (mod(n_tasks, nprows) == 0) exit
    enddo
    this%nprows = nprows
    this%npcols = n_tasks/this%nprows
    if (present(comm)) then
        this%ctx = comm
    else
        call BLACS_GET(0, 0, this%ctx)
    end if
    call BLACS_GRIDINIT(this%ctx, 'R', this%nprows, this%npcols)
    call BLACS_GRIDINFO( &
        this%ctx, this%nprows, this%npcols, this%my_prow, this%my_pcol &
    )
end subroutine

! TODO this should be made a destructor once support for gfortran 4.9 is dropped
subroutine mbd_blacs_grid_destroy(this)
    class(mbd_blacs_grid), intent(inout) :: this

    call BLACS_GRIDEXIT(this%ctx)
end subroutine

subroutine mbd_blacs_desc_init(this, n_atoms, grid)
    class(mbd_blacs_desc), intent(out) :: this
    type(mbd_blacs_grid), intent(in) :: grid
    integer, intent(in) :: n_atoms

    integer :: blocksize, my_nratoms, my_ncatoms, ierr

    this%ctx = grid%ctx
    this%n_atoms = n_atoms
    blocksize = 3
    my_nratoms = NUMROC(n_atoms, blocksize/3, grid%my_prow, 0, grid%nprows)
    my_ncatoms = NUMROC(n_atoms, blocksize/3, grid%my_pcol, 0, grid%npcols)
    call DESCINIT( &
        this%desc, 3*n_atoms, 3*n_atoms, blocksize, blocksize, 0, 0, &
        grid%ctx, 3*my_nratoms, ierr &
    )
    this%i_atom = idx_map( &
        grid%my_prow, grid%nprows, n_atoms, blocksize/3, my_nratoms &
    )
    this%j_atom = idx_map( &
        grid%my_pcol, grid%npcols, n_atoms, blocksize/3, my_ncatoms &
    )
end subroutine

function idx_map(my_task, n_tasks, n, blocksize, nidx)
    integer, intent(in) :: my_task, n_tasks, n, blocksize, nidx
    integer :: idx_map(nidx)

    integer :: i, i_block, n_in_block, my_i

    i_block = 0
    n_in_block = 0
    my_i = 1
    do i = 1, n
        if (mod(i_block, n_tasks) == my_task) then
            idx_map(my_i) = i
            my_i = my_i + 1
        end if
        n_in_block = n_in_block + 1
        if (n_in_block == blocksize) then
            n_in_block = 0
            i_block = i_block + 1
        end if
    end do
end function

subroutine all_reduce_real_1d(A, blacs)
    real(dp), intent(inout) :: A(:)
    type(mbd_blacs_desc), intent(in) :: blacs

    if (blacs%ctx == -1) return
    call DGSUM2D(blacs%ctx, 'A', ' ', size(A), 1, A, size(A), -1, -1)
end subroutine

subroutine all_reduce_real_2d(A, blacs)
    real(dp), intent(inout) :: A(:, :)
    type(mbd_blacs_desc), intent(in) :: blacs

    if (blacs%ctx == -1) return
    call DGSUM2D( &
        blacs%ctx, 'A', ' ', size(A, 1), size(A, 2), A, size(A, 1), -1, -1 &
    )
end subroutine

subroutine all_reduce_complex_1d(A, blacs)
    complex(dp), intent(inout) :: A(:)
    type(mbd_blacs_desc), intent(in) :: blacs

    if (blacs%ctx == -1) return
    call ZGSUM2D(blacs%ctx, 'A', ' ', size(A), 1, A, size(A), -1, -1)
end subroutine

subroutine all_reduce_complex_2d(A, blacs)
    complex(dp), intent(inout) :: A(:, :)
    type(mbd_blacs_desc), intent(in) :: blacs

    if (blacs%ctx == -1) return
    call ZGSUM2D( &
        blacs%ctx, 'A', ' ', size(A, 1), size(A, 2), A, size(A, 1), -1, -1 &
    )
end subroutine

end module