! PhasedArray.f90
! Compiled User-Defined Function (UDF) for ElmerFEM
! Pure top-level functions reading directly from Model memory (Segfault Safe)

FUNCTION PressureReal(Model, n, t) RESULT(P_re)
  USE DefUtils
  IMPLICIT NONE
  
  TYPE(Model_t) :: Model
  INTEGER :: n
  REAL(KIND=dp) :: t, P_re
  
  REAL(KIND=dp), PARAMETER :: C0 = 343.0_dp
  REAL(KIND=dp), PARAMETER :: FREQ = 40000.0_dp
  REAL(KIND=dp), PARAMETER :: OMEGA = 2.0_dp * PI * FREQ
  REAL(KIND=dp), PARAMETER :: K_WAVE = OMEGA / C0
  REAL(KIND=dp), PARAMETER :: P0 = 100.0_dp
  REAL(KIND=dp), PARAMETER :: Z_FOCAL = 0.05_dp
  REAL(KIND=dp), PARAMETER :: ARRAY_LIMIT = 0.042_dp

  REAL(KIND=dp) :: x, y, r, r_max, phase

  ! Safe memory access directly from the FEM node struct
  x = Model % Nodes % x(n)
  y = Model % Nodes % y(n)

  IF (ABS(x) <= ARRAY_LIMIT .AND. ABS(y) <= ARRAY_LIMIT) THEN
    r = SQRT(x**2 + y**2 + Z_FOCAL**2)
    r_max = SQRT(2.0_dp * ARRAY_LIMIT**2 + Z_FOCAL**2)
    phase = K_WAVE * (r_max - r)
    P_re = P0 * COS(phase)
  ELSE
    P_re = 0.0_dp
  END IF
END FUNCTION PressureReal

FUNCTION PressureImag(Model, n, t) RESULT(P_im)
  USE DefUtils
  IMPLICIT NONE
  
  TYPE(Model_t) :: Model
  INTEGER :: n
  REAL(KIND=dp) :: t, P_im
  
  REAL(KIND=dp), PARAMETER :: C0 = 343.0_dp
  REAL(KIND=dp), PARAMETER :: FREQ = 40000.0_dp
  REAL(KIND=dp), PARAMETER :: OMEGA = 2.0_dp * PI * FREQ
  REAL(KIND=dp), PARAMETER :: K_WAVE = OMEGA / C0
  REAL(KIND=dp), PARAMETER :: P0 = 100.0_dp
  REAL(KIND=dp), PARAMETER :: Z_FOCAL = 0.05_dp
  REAL(KIND=dp), PARAMETER :: ARRAY_LIMIT = 0.042_dp

  REAL(KIND=dp) :: x, y, r, r_max, phase

  x = Model % Nodes % x(n)
  y = Model % Nodes % y(n)

  IF (ABS(x) <= ARRAY_LIMIT .AND. ABS(y) <= ARRAY_LIMIT) THEN
    r = SQRT(x**2 + y**2 + Z_FOCAL**2)
    r_max = SQRT(2.0_dp * ARRAY_LIMIT**2 + Z_FOCAL**2)
    phase = K_WAVE * (r_max - r)
    P_im = P0 * SIN(phase)
  ELSE
    P_im = 0.0_dp
  END IF
END FUNCTION PressureImag