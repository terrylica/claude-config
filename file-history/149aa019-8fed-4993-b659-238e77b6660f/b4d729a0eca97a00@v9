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
//| Find the mother bar index for an inside bar sequence             |
//| Mother bar = the OUTERMOST expanding bar that contains currentBar|
//| Returns: Index of mother bar, or -1 if not found                 |
//+------------------------------------------------------------------+
int FindMotherBar(const double &high[], const double &low[], int currentBar, int rates_total)
{
   int lastContainingBar = -1;

   // Walk backward to find the OUTERMOST bar that contains currentBar
   for(int i = currentBar + 1; i < rates_total; i++)
   {
      // Check if bar i contains currentBar
      if(high[currentBar] <= high[i] && low[currentBar] >= low[i])
      {
         // Check if bar i is an expansion bar (NOT inside bar i+1)
         if(i >= rates_total - 1 ||
            high[i] > high[i+1] || low[i] < low[i+1])
         {
            // This is an expanding bar that contains currentBar
            // But keep looking for an even larger one
            lastContainingBar = i;
         }
      }
      else
      {
         // Bar i doesn't contain currentBar
         // Return the last bar that did contain it
         if(lastContainingBar >= 0)
            return lastContainingBar;
         else if(i > currentBar + 1)
            return i - 1;
         else
            return -1;
      }
   }

   // Reached end of data
   if(lastContainingBar >= 0)
      return lastContainingBar;

   return rates_total - 1;
}

//+------------------------------------------------------------------+
//| Count consecutive inside bars from mother bar to current bar     |
//| All bars within mother bar's high/low range are counted          |
//| Returns: Total number of bars inside mother range (1-based)      |
//+------------------------------------------------------------------+
int CountConsecutiveInsideBars(const double &high[], const double &low[], int currentBar, int motherBarIndex)
{
   int consecutiveCount = 0;

   // Count all bars from mother bar - 1 down to current bar that are within mother range
   for(int j = motherBarIndex - 1; j >= currentBar; j--)
   {
      // Check if bar j is inside the mother bar's range
      if(high[j] <= high[motherBarIndex] && low[j] >= low[motherBarIndex])
         consecutiveCount++;
      // Don't break - continue counting even if there are gaps (bars outside mother range)
   }

   return consecutiveCount;
}

//+------------------------------------------------------------------+
//| Set inside bar signal as purple colored bar                      |
//| Only colors the Nth consecutive inside bar (relative to mother)  |
//| Requires: Global buffers and input parameters from parent        |
//| Priority system: Only colors bar if not already colored          |
//+------------------------------------------------------------------+
void SetInsideBarSignal(int bar, bool isBullish, const double &high[], const double &low[], int rates_total)
{
   // Find the mother bar (larger bar preceding the inside bar sequence)
   int motherBarIndex = FindMotherBar(high, low, bar, rates_total);

   // If no mother bar found, skip
   if(motherBarIndex < 0)
      return;

   // Verify current bar is still inside the mother bar's range
   if(high[bar] > high[motherBarIndex] || low[bar] < low[motherBarIndex])
      return;

   // Count consecutive inside bars from mother bar to current bar
   int consecutiveCount = CountConsecutiveInsideBars(high, low, bar, motherBarIndex);

   // Only color if this is the Nth or later consecutive inside bar
   if(consecutiveCount < InpInsideBarThreshold)
      return;

   // Three-tier coloring system
   if(InpShowColorBars) {
      if(BufferColorIndex[bar] == COLOR_NONE) {
         // Inside bar only → Purple
         BufferColorIndex[bar] = CLR_INSIDE_BAR;
      } else if(BufferColorIndex[bar] == CLR_BULLISH || BufferColorIndex[bar] == CLR_BEARISH) {
         // Both contraction AND inside bar → White
         BufferColorIndex[bar] = CLR_BOTH;
      }
   }
}
//+------------------------------------------------------------------+
