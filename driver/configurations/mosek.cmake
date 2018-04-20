set(MOSEKLM_LICENSE_FILE "/tmp/mosek.lic")
file(REMOVE "${MOSEKLM_LICENSE_FILE}")

message(STATUS "Downloading MOSEK license file from AWS S3...")
execute_process(
  COMMAND "${DASHBOARD_AWS_COMMAND}" s3 cp
    s3://drake-provisioning/mosek/mosek.lic "${MOSEKLM_LICENSE_FILE}"
  RESULT_VARIABLE DASHBOARD_AWS_S3_RESULT_VARIABLE
  OUTPUT_VARIABLE DASHBOARD_AWS_S3_OUTPUT_VARIABLE
  ERROR_VARIABLE DASHBOARD_AWS_S3_OUTPUT_VARIABLE)
list(APPEND DASHBOARD_TEMPORARY_FILES MOSEKLM_LICENSE_FILE)
message("${DASHBOARD_AWS_S3_OUTPUT_VARIABLE}")

if(NOT EXISTS "${MOSEKLM_LICENSE_FILE}")
  fatal("MOSEK license file was NOT found")
endif()

set(ENV{MOSEKLM_LICENSE_FILE} "${MOSEKLM_LICENSE_FILE}")
