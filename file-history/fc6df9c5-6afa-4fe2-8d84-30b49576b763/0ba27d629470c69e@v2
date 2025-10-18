//+------------------------------------------------------------------+
//| Test indicator to verify custom include resolution              |
//+------------------------------------------------------------------+
#property indicator_separate_window
#property indicator_buffers 1
#property indicator_plots   1

#include <DataExport/DataExportCore.mqh>

double buffer[];

int OnInit()
{
   SetIndexBuffer(0, buffer, INDICATOR_DATA);
   return(INIT_SUCCEEDED);
}

int OnCalculate(const int rates_total,
                const int prev_calculated,
                const int begin,
                const double &price[])
{
   return(rates_total);
}
