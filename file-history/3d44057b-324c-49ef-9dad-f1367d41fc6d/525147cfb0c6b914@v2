#property script_show_inputs
#property strict

#include <DataExport/DataExportCore.mqh>
#include <DataExport/modules/RSIModule.mqh>

input string          InpSymbol     = "EURUSD";
input ENUM_TIMEFRAMES InpTimeframe  = PERIOD_M1;
input int             InpBars       = 5000;
input bool            InpUseRSI     = true;
input int             InpRSIPeriod  = 14;
input string          InpOutputName = "";

void OnStart()
  {
   string symbol=InpSymbol;
   StringTrimLeft(symbol);
   StringTrimRight(symbol);
   if(StringLen(symbol)==0)
     {
      Print("Symbol input is empty");
      return;
     }
   if(!SymbolSelect(symbol,true))
     {
      PrintFormat("SymbolSelect failed for %s (error %d)",symbol,GetLastError());
      return;
     }

   BarSeries series;
   if(!LoadRates(symbol,InpTimeframe,InpBars,series))
     {
      Print("LoadRates failed");
      return;
     }
   if(series.count<=0)
     {
      Print("No bars returned");
      return;
     }

   IndicatorColumn columns[];
   int columnCount=0;

   if(InpUseRSI)
     {
      IndicatorColumn rsiColumn;
      string rsiError="";
      if(!RSIModule_Load(symbol,InpTimeframe,series.count,InpRSIPeriod,rsiColumn,rsiError))
        {
         PrintFormat("RSI module failed: %s",rsiError);
         return;
        }
      ArrayResize(columns,columnCount+1);
      columns[columnCount]=rsiColumn;
      columnCount++;
     }

   string filename=InpOutputName;
   if(StringLen(filename)==0)
      filename=StringFormat("Export_%s_%s.csv",symbol,EnumToString(InpTimeframe));

   int handle;
   if(!OpenCsv(filename,handle))
     {
      PrintFormat("Failed to open output file %s (error %d)",filename,GetLastError());
      return;
     }

   string baseHeaders[8]={"time","open","high","low","close","tick_volume","spread","real_volume"};
   WriteCsvHeader(handle,baseHeaders,columns,columnCount);
   if(!WriteCsvRows(handle,series,columns,columnCount))
     {
      FileClose(handle);
      Print("Failed to write CSV rows");
      return;
     }
   FileClose(handle);
   PrintFormat("Export complete: %d bars for %s %s -> %s",series.count,symbol,EnumToString(InpTimeframe),filename);
  }
