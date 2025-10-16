//+------------------------------------------------------------------+
//|                                             PatternHelpers.mqh   |
//|                                                        Terry Li |
//|                         Common helper functions for patterns     |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Check if all bars in the pattern have the same direction         |
//+------------------------------------------------------------------+
bool CheckSameDirection(const double &open[], const double &close[], int startBar, int count, bool isBullish)
{
   for(int j = 1; j < count; j++)
   {
      bool isCurrentBarBullish = close[startBar + j] > open[startBar + j];
      if(isCurrentBarBullish != isBullish)
         return false;
   }
   return true;
}

//+------------------------------------------------------------------+
//| Check if we have consecutive contractions in body size           |
//+------------------------------------------------------------------+
bool CheckConsecutiveContractions(const double &bodySizes[], int startBar, int count)
{
   for(int j = 0; j < count - 1; j++)
   {
      // For a contraction, current bar should have smaller body than previous
      if(bodySizes[startBar + j] >= bodySizes[startBar + j + 1])
         return false;
   }
   return true;
}

//+------------------------------------------------------------------+
//| Check if we have consecutive expansions in body size             |
//+------------------------------------------------------------------+
bool CheckConsecutiveExpansions(const double &bodySizes[], int startBar, int count)
{
   for(int j = 0; j < count - 1; j++)
   {
      // For an expansion, current bar should have larger body than previous
      if(bodySizes[startBar + j] <= bodySizes[startBar + j + 1])
         return false;
   }
   return true;
}
//+------------------------------------------------------------------+
