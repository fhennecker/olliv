#include "math.h"
#include <sqlite3ext.h>
#include <stdlib.h> 
SQLITE_EXTENSION_INIT1

static void distance(sqlite3_context *context, int argc, sqlite3_value **argv) {
    double gpsy1 = sqlite3_value_double(argv[0]) * M_PI / 180; // lat in radians
    double gpsx1 = sqlite3_value_double(argv[1]) * M_PI / 180; // long in radians
    double gpsy2 = sqlite3_value_double(argv[2]) * M_PI / 180; // lat in radians
    double gpsx2 = sqlite3_value_double(argv[3]) * M_PI / 180; // long in radians
    double r = 6371.0; // earth's radius in kilometers
    double a, c, distance;

    a = pow(sin((gpsx2-gpsx1)/2),2) + pow(sin((gpsy2-gpsy1)/2), 2) * cos(gpsx1) * cos(gpsx2);
    c = 2 * atan2(sqrt(a), sqrt(1-a));
    distance = r*c;
    sqlite3_result_double(context, distance);
}

#ifdef _WIN32
__declspec(dllexport)
#endif
int sqlite3_distance_init(
  sqlite3 *db, 
  char **pzErrMsg, 
  const sqlite3_api_routines *pApi
){
  int rc = SQLITE_OK;
  SQLITE_EXTENSION_INIT2(pApi);
  sqlite3_create_function_v2(db, "distance", 4, SQLITE_ANY, NULL, distance, NULL, NULL, NULL);
  return rc;
}