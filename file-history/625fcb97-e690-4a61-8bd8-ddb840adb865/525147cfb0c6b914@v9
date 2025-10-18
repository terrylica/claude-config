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
//| Returns working copies of parameters (inputs are const)          |
//+------------------------------------------------------------------+
bool LoadConfigFromFile(string &symbol, ENUM_TIMEFRAMES &timeframe, int &bars,
                        bool &useRSI, int &rsiPeriod,
                        bool &useSMA, int &smaPeriod,
                        bool &useLaguerreRSI, string &laguerreInstanceID,
                        int &laguerreAtrPeriod, int &laguerreSmoothPeriod,
                        ENUM_MA_METHOD &laguerreSmoothMethod, string &outputName)
  {
   string configFile="export_config.txt";
   int handle=FileOpen(configFile,FILE_READ|FILE_TXT|FILE_ANSI);

   if(handle==INVALID_HANDLE)
     {
      // Config file not found - return false to use input parameters
      int error=GetLastError();
      PrintFormat("WARNING: Could not open config file '%s' (error %d) - using input parameters",
                  configFile,error);
      return false;
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

      // Override working variables (NOT input constants)
      if(key=="InpSymbol")              { symbol=value; linesLoaded++; }
      else if(key=="InpTimeframe")      { timeframe=(ENUM_TIMEFRAMES)StringToInteger(value); linesLoaded++; }
      else if(key=="InpBars")           { bars=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpUseRSI")         { useRSI=(value=="true"); linesLoaded++; }
      else if(key=="InpRSIPeriod")      { rsiPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpUseSMA")         { useSMA=(value=="true"); linesLoaded++; }
      else if(key=="InpSMAPeriod")      { smaPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpUseLaguerreRSI") { useLaguerreRSI=(value=="true"); linesLoaded++; }
      else if(key=="InpLaguerreInstanceID")   { laguerreInstanceID=value; linesLoaded++; }
      else if(key=="InpLaguerreAtrPeriod")    { laguerreAtrPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpLaguerreSmoothPeriod") { laguerreSmoothPeriod=(int)StringToInteger(value); linesLoaded++; }
      else if(key=="InpLaguerreSmoothMethod") { laguerreSmoothMethod=(ENUM_MA_METHOD)StringToInteger(value); linesLoaded++; }
      else if(key=="InpOutputName")     { outputName=value; linesLoaded++; }
      else
         PrintFormat("WARNING: Unknown config key (skipped): %s",key);
     }

   FileClose(handle);
   PrintFormat("=== Config loaded: %d parameters from %s ===",linesLoaded,configFile);
   return true;
  }

void OnStart()
  {
   // Create working copies of input parameters (inputs are const, can't be modified)
   string symbol=InpSymbol;
   ENUM_TIMEFRAMES timeframe=InpTimeframe;
   int bars=InpBars;
   bool useRSI=InpUseRSI;
   int rsiPeriod=InpRSIPeriod;
   bool useSMA=InpUseSMA;
   int smaPeriod=InpSMAPeriod;
   bool useLaguerreRSI=InpUseLaguerreRSI;
   string laguerreInstanceID=InpLaguerreInstanceID;
   int laguerreAtrPeriod=InpLaguerreAtrPeriod;
   int laguerreSmoothPeriod=InpLaguerreSmoothPeriod;
   ENUM_MA_METHOD laguerreSmoothMethod=InpLaguerreSmoothMethod;
   string outputName=InpOutputName;

   // Try to load config from file (optional - overrides working copies)
   bool configLoaded=LoadConfigFromFile(symbol,timeframe,bars,useRSI,rsiPeriod,
                                         useSMA,smaPeriod,useLaguerreRSI,
                                         laguerreInstanceID,laguerreAtrPeriod,
                                         laguerreSmoothPeriod,laguerreSmoothMethod,
                                         outputName);

   // DEBUG: Log final parameters (after config override)
   Print("=== ExportAligned.mq5 Final Parameters ===");
   PrintFormat("Symbol: '%s'",symbol);
   PrintFormat("Timeframe: %s (%d)",EnumToString(timeframe),timeframe);
   PrintFormat("Bars: %d",bars);
   PrintFormat("UseRSI: %s",useRSI?"true":"false");
   PrintFormat("RSIPeriod: %d",rsiPeriod);
   PrintFormat("UseSMA: %s",useSMA?"true":"false");
   PrintFormat("SMAPeriod: %d",smaPeriod);
   PrintFormat("UseLaguerreRSI: %s",useLaguerreRSI?"true":"false");
   PrintFormat("LaguerreInstanceID: '%s'",laguerreInstanceID);
   PrintFormat("LaguerreAtrPeriod: %d",laguerreAtrPeriod);
   PrintFormat("LaguerreSmoothPeriod: %d",laguerreSmoothPeriod);
   PrintFormat("LaguerreSmoothMethod: %s (%d)",EnumToString(laguerreSmoothMethod),laguerreSmoothMethod);
   PrintFormat("OutputName: '%s'",outputName);
   Print("========================================");
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
   datetime from=TimeCurrent()-PeriodSeconds(timeframe)*1000;
   int attempts=0;
   int maxAttempts=50;  // 50 * 100ms = 5 seconds

   while(attempts<maxAttempts)
     {
      datetime time[];
      int copied=CopyTime(symbol,timeframe,0,1,time);
      if(copied>0)
         break;

      Sleep(100);
      attempts++;
     }

   if(attempts>=maxAttempts)
     {
      PrintFormat("ERROR: History download timeout for %s %s after %d ms",
                  symbol,EnumToString(timeframe),maxAttempts*100);
      return;
     }

   PrintFormat("History available for %s %s (waited %d ms)",
               symbol,EnumToString(timeframe),attempts*100);

   BarSeries series;
   if(!LoadRates(symbol,timeframe,bars,series))
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

   if(useRSI)
     {
      IndicatorColumn rsiColumn;
      string rsiError="";
      if(!RSIModule_Load(symbol,timeframe,series.count,rsiPeriod,rsiColumn,rsiError))
        {
         PrintFormat("RSI module failed: %s",rsiError);
         return;
        }
      ArrayResize(columns,columnCount+1);
      columns[columnCount]=rsiColumn;
      columnCount++;
     }

   if(useSMA)
     {
      IndicatorColumn smaColumn;
      string smaError="";
      if(!SMAModule_Load(symbol,timeframe,series.count,smaPeriod,smaColumn,smaError))
        {
         PrintFormat("SMA module failed: %s",smaError);
         return;
        }
      ArrayResize(columns,columnCount+1);
      columns[columnCount]=smaColumn;
      columnCount++;
     }

   if(useLaguerreRSI)
     {
      IndicatorColumn laguerreColumn, signalColumn, adaptivePeriodColumn, atrColumn;
      string laguerreError="";
      if(!LaguerreRSIModule_Load(
            symbol,
            timeframe,
            series.count,
            laguerreInstanceID,
            laguerreAtrPeriod,
            laguerreSmoothPeriod,
            laguerreSmoothMethod,
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

   string filename=outputName;
   if(StringLen(filename)==0)
      filename=StringFormat("Export_%s_%s.csv",symbol,EnumToString(timeframe));

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
   PrintFormat("Export complete: %d bars for %s %s -> %s",series.count,symbol,EnumToString(timeframe),filename);
  }
