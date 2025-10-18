//+------------------------------------------------------------------+
//| TestConfigReader.mq5 - Spike test for file-based config          |
//| Tests: FileOpen, FileReadString, StringSplit, type conversions   |
//+------------------------------------------------------------------+
#property script_show_inputs
#property strict

//+------------------------------------------------------------------+
//| Script program start function                                     |
//+------------------------------------------------------------------+
void OnStart()
  {
   Print("=== Spike Test: Config File Reading ===");

   // Test 1: Can we open files from MQL5/Files/?
   int handle=FileOpen("test_config.txt",FILE_READ|FILE_TXT|FILE_ANSI);
   if(handle==INVALID_HANDLE)
     {
      PrintFormat("FAIL: Cannot open file (error %d)",GetLastError());
      return;
     }
   Print("SUCCESS: File opened");

   // Test 2: Can we read line by line?
   int lineCount=0;
   while(!FileIsEnding(handle))
     {
      string line=FileReadString(handle);
      lineCount++;

      // Skip empty lines and comments
      StringTrimLeft(line);
      StringTrimRight(line);
      if(StringLen(line)==0 || StringGetCharacter(line,0)=='#')
        {
         PrintFormat("  Line %d: Skipped (comment/empty)",lineCount);
         continue;
        }

      // Test 3: Can we parse key=value with StringSplit?
      string parts[];
      int splitCount=StringSplit(line,'=',parts);
      if(splitCount!=2)
        {
         PrintFormat("  Line %d: FAIL - Invalid format: %s",lineCount,line);
         continue;
        }

      string key=parts[0];
      string value=parts[1];
      StringTrimLeft(key);
      StringTrimRight(key);
      StringTrimLeft(value);
      StringTrimRight(value);

      PrintFormat("  Line %d: SUCCESS - %s = %s",lineCount,key,value);

      // Test 4: Can we convert types correctly?
      if(key=="InpBars" || key=="InpTimeframe" || key=="InpSMAPeriod")
        {
         int intValue=(int)StringToInteger(value);
         PrintFormat("    -> Type conversion (int): %d",intValue);
        }

      if(key=="InpUseSMA" || key=="InpUseRSI")
        {
         bool boolValue=(value=="true");
         PrintFormat("    -> Type conversion (bool): %s",boolValue?"true":"false");
        }
     }

   FileClose(handle);
   PrintFormat("=== Spike Test Complete: %d lines processed ===",lineCount);
  }
//+------------------------------------------------------------------+
