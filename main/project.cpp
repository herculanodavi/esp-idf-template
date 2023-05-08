#include <cstdlib>

#include "esp_log.h"

extern "C" void app_main(void)
{
  int const integer = 0;
  ESP_LOGI("MAIN", "%d is an integer", integer);
}
