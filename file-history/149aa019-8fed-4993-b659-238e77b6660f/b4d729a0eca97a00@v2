//+------------------------------------------------------------------+
//|                                           CandlePatterns.mqh     |
//|                                                        Terry Li |
//|                  Candlestick pattern detection (inside bar, etc) |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Check if current bar is an inside bar                            |
//| Inside bar: High <= prev high AND Low >= prev low                |
//+------------------------------------------------------------------+
bool CheckInsideBar(const double &high[], const double &low[], int bar)
{
   // Need at least one previous bar
   if(bar >= ArraySize(high) - 1)
      return false;

   // Inside bar condition:
   // Current bar's range is completely within previous bar's range
   if(high[bar] <= high[bar+1] && low[bar] >= low[bar+1])
      return true;

   return false;
}

//+------------------------------------------------------------------+
//| Set inside bar signal based on pattern direction                 |
//| Requires: Global buffers and input parameters from parent        |
//+------------------------------------------------------------------+
void SetInsideBarSignal(int bar, bool isBullish, const double &high[], const double &low[])
{
   if(isBullish)
   {
      // Set bullish inside bar signal (dot above high)
      if(InpShowInsideBarDots)
      {
         BufferInsideBarBullishSignal[bar] = high[bar] + (15 * Point());
      }
   }
   else
   {
      // Set bearish inside bar signal (dot below low)
      if(InpShowInsideBarDots)
      {
         BufferInsideBarBearishSignal[bar] = low[bar] - (15 * Point());
      }
   }
}
//+------------------------------------------------------------------+
