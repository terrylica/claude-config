//+------------------------------------------------------------------+
//|                                              SimpleSMA_Test.mq5 |
//|                                       Test indicator for workflow|
//|                                                                  |
//+------------------------------------------------------------------+
#property copyright "Test"
#property link      ""
#property version   "1.00"
#property indicator_chart_window
#property indicator_buffers 1
#property indicator_plots   1

#property indicator_label1  "SMA"
#property indicator_type1   DRAW_LINE
#property indicator_color1  clrBlue
#property indicator_width1  2

input int InpPeriod = 14;  // SMA Period

double SMABuffer[];

//+------------------------------------------------------------------+
//| Custom indicator initialization function                         |
//+------------------------------------------------------------------+
int OnInit()
{
    SetIndexBuffer(0, SMABuffer, INDICATOR_DATA);
    IndicatorSetString(INDICATOR_SHORTNAME, StringFormat("SMA(%d)", InpPeriod));
    IndicatorSetInteger(INDICATOR_DIGITS, _Digits);
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Custom indicator iteration function                              |
//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
{
    int start = InpPeriod - 1;
    if(prev_calculated == 0)
    {
        // Initialize buffer with zeros
        ArrayInitialize(SMABuffer, 0.0);
    }
    else
    {
        start = prev_calculated - 1;
    }

    // Calculate SMA for each bar
    for(int i = start; i < rates_total && !IsStopped(); i++)
    {
        double sum = 0.0;
        for(int j = 0; j < InpPeriod; j++)
        {
            sum += close[i - j];
        }
        SMABuffer[i] = sum / InpPeriod;
    }

    return(rates_total);
}
//+------------------------------------------------------------------+
