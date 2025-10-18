
#ifndef __SMA_MODULE_MQH__
#define __SMA_MODULE_MQH__

#include "..\\DataExportCore.mqh"

bool SMAModule_Load(const string symbol,
                    const ENUM_TIMEFRAMES timeframe,
                    const int bars,
                    const int period,
                    IndicatorColumn &column,
                    string &errorMessage)
  {
   column.header=StringFormat("SMA_%d",period);
   column.digits=5;
   ArrayResize(column.values,bars);
   ArraySetAsSeries(column.values,true);

   int handle=iCustom(symbol,timeframe,"Custom\\PythonInterop\\SimpleSMA_Test",period);
   if(handle==INVALID_HANDLE)
     {
      errorMessage="SimpleSMA_Test handle creation failed";
      return(false);
     }
   int copied=CopyBuffer(handle,0,0,bars,column.values);
   IndicatorRelease(handle);
   if(copied!=bars)
     {
      errorMessage=StringFormat("SMA CopyBuffer expected %d bars, received %d",bars,copied);
      return(false);
     }
   return(true);
  }

#endif // __SMA_MODULE_MQH__
