#property script_show_inputs
#property strict

#include <DataExport/DataExportCore.mqh>
#include <DataExport/modules/RSIModule.mqh>
#include <DataExport/modules/SMAModule.mqh>
#include <DataExport/modules/LaguerreRSIModule.mqh>

input string          InpSymbol             = "EURUSD";
input ENUM_TIMEFRAMES InpTimeframe          = PERIOD_M1;
input int             InpBars               = 5000;
input bool            InpUseRSI             = true;
input int             InpRSIPeriod          = 14;
input bool            InpUseSMA             = false;
input int             InpSMAPeriod          = 14;
input bool            InpUseLaguerreRSI     = false;
input string          InpLaguerreInstanceID = "A";
input int             InpLaguerreAtrPeriod  = 32;
input int             InpLaguerreSmoothPeriod = 5;
input ENUM_MA_METHOD  InpLaguerreSmoothMethod = MODE_EMA;
input string          InpOutputName         = "";

//+------------------------------------------------------------------+
//| Load configuration from file (optional, graceful degradation)    |
//+------------------------------------------------------------------+
void LoadConfigFromFile()
  {
   string configFile="export_config.txt";
   int handle=FileOpen(configFile,FILE_READ|FILE_TXT|FILE_ANSI);

   if(handle==INVALID_HANDLE)
     {
      // Config file not found - silently continue with input parameters
      return;
     }

   Print("=== Loading configuration from ",configFile," ===");
   int linesLoaded=0;

   while(!FileIsEnding(handle))
     {
      string line=FileReadString(handle);
      StringTrimLeft(line);
      StringTrimRight(line);

      // Skip empty lines and comments
      if(StringLen(line)==0 || StringGetCharacter(line,0)=='#')
         continue;

      // Parse key=value
      string parts[];
      if(StringSplit(line,'=',parts)!=2)
        {
         PrintFormat("WARNING: Invalid config line (skipped): %s",line);
         continue;
        }

      string key=parts[0];
      string value=parts[1];
      StringTrimLeft(key);
      StringTrimRight(key);
      StringTrimLeft(value);
      StringTrimRight(value);

      // Override input parameters
      if(key=="InpSymbol")              { InpSymbol=value; linesLoaded++; }
      else if(key=="InpTimeframe")      { InpTimeframe=(ENUM_TIMEFRAMES)StringToInteger(value); linesLoaded++; }
      else if(key=="InpBars")           { InpBars=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpUseRSI")         { InpUseRSI=(value=="true"); linesLoaded++; }
      else if(key=="InpRSIPeriod")      { InpRSIPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpUseSMA")         { InpUseSMA=(value=="true"); linesLoaded++; }
      else if(key=="InpSMAPeriod")      { InpSMAPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpUseLaguerreRSI") { InpUseLaguerreRSI=(value=="true"); linesLoaded++; }
      else if(key=="InpLaguerreInstanceID")   { InpLaguerreInstanceID=value; linesLoaded++; }
      else if(key=="InpLaguerreAtrPeriod")    { InpLaguerreAtrPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpLaguerreSmoothPeriod") { InpLaguerreSmoothPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpLaguerreSmoothMethod") { InpLaguerreSmoothMethod=(ENUM_MA_METHOD)StringToInteger(value); linesLoaded++; }
      else if(key=="InpOutputName")     { InpOutputName=value; linesLoaded++; }
      else
         PrintFormat("WARNING: Unknown config key (skipped): %s",key);
     }

   FileClose(handle);
   PrintFormat("=== Config loaded: %d parameters from %s ===",linesLoaded,configFile);
  }

void OnStart()
  {
   // Try to load config from file (optional - falls back to input parameters)
   LoadConfigFromFile();

   // DEBUG: Log all input parameters to diagnose parameter passing
   Print("=== ExportAligned.mq5 Input Parameters ===");
   PrintFormat("InpSymbol: '%s'",InpSymbol);
   PrintFormat("InpTimeframe: %s (%d)",EnumToString(InpTimeframe),InpTimeframe);
   PrintFormat("InpBars: %d",InpBars);
   PrintFormat("InpUseRSI: %s",InpUseRSI?"true":"false");
   PrintFormat("InpRSIPeriod: %d",InpRSIPeriod);
   PrintFormat("InpUseSMA: %s",InpUseSMA?"true":"false");
   PrintFormat("InpSMAPeriod: %d",InpSMAPeriod);
   PrintFormat("InpUseLaguerreRSI: %s",InpUseLaguerreRSI?"true":"false");
   PrintFormat("InpLaguerreInstanceID: '%s'",InpLaguerreInstanceID);
   PrintFormat("InpLaguerreAtrPeriod: %d",InpLaguerreAtrPeriod);
   PrintFormat("InpLaguerreSmoothPeriod: %d",InpLaguerreSmoothPeriod);
   PrintFormat("InpLaguerreSmoothMethod: %s (%d)",EnumToString(InpLaguerreSmoothMethod),InpLaguerreSmoothMethod);
   PrintFormat("InpOutputName: '%s'",InpOutputName);
   Print("========================================");

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
      PrintFormat("ERROR: SymbolSelect failed for %s (error %d)",symbol,GetLastError());
      return;
     }

   Print("Symbol selected: ",symbol);

   // Wait for history download (Solution A pattern - max 5 seconds)
   datetime from=TimeCurrent()-PeriodSeconds(InpTimeframe)*1000;
   int attempts=0;
   int maxAttempts=50;  // 50 * 100ms = 5 seconds

   while(attempts<maxAttempts)
     {
      datetime time[];
      int copied=CopyTime(symbol,InpTimeframe,0,1,time);
      if(copied>0)
         break;

      Sleep(100);
      attempts++;
     }

   if(attempts>=maxAttempts)
     {
      PrintFormat("ERROR: History download timeout for %s %s after %d ms",
                  symbol,EnumToString(InpTimeframe),maxAttempts*100);
      return;
     }

   PrintFormat("History available for %s %s (waited %d ms)",
               symbol,EnumToString(InpTimeframe),attempts*100);

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

   if(InpUseSMA)
     {
      IndicatorColumn smaColumn;
      string smaError="";
      if(!SMAModule_Load(symbol,InpTimeframe,series.count,InpSMAPeriod,smaColumn,smaError))
        {
         PrintFormat("SMA module failed: %s",smaError);
         return;
        }
      ArrayResize(columns,columnCount+1);
      columns[columnCount]=smaColumn;
      columnCount++;
     }

   if(InpUseLaguerreRSI)
     {
      IndicatorColumn laguerreColumn, signalColumn, adaptivePeriodColumn, atrColumn;
      string laguerreError="";
      if(!LaguerreRSIModule_Load(
            symbol,
            InpTimeframe,
            series.count,
            InpLaguerreInstanceID,
            InpLaguerreAtrPeriod,
            InpLaguerreSmoothPeriod,
            InpLaguerreSmoothMethod,
            laguerreColumn,
            signalColumn,
            adaptivePeriodColumn,
            atrColumn,
            laguerreError))
        {
         PrintFormat("Laguerre RSI module failed: %s",laguerreError);
         return;
        }
      ArrayResize(columns,columnCount+4);
      columns[columnCount]=laguerreColumn;
      columnCount++;
      columns[columnCount]=signalColumn;
      columnCount++;
      columns[columnCount]=adaptivePeriodColumn;
      columnCount++;
      columns[columnCount]=atrColumn;
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
