VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Sheet1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

Private Sub Worksheet_Calculate()
'needs error handling

    'enters this loop when any calculation that changes value in cell B8
    If Range("actualSavings").Value <> PrevVal Then
        
        Dim x, a, h, k
        'Const ms As Double = 0.000000011574
        
        'hide splat graphic
        Range("splat_x").Value = -100
        Range("splat_y").Value = -100
        
        'define parabola based on magnitude of kwh/joules
        a = Range("_a").Value 'stretch
            If a > -0.004 Then a = -0.004
        h = Range("_h").Value 'midpoint
            If h > 500 Then h = 500
        k = Range("_k").Value 'height
            If k > 1000 Then k = 1000
                
        'reset tomato graphic
        Range("_x").Value = 0
        Range("_y").Value = 0
        Calculate 'seems to work faster than Application.ScreenUpdating = True
        Sleep (1000)
        'Application.Wait Now + ms * 1000
        Calculate
        Sleep (1000)
        
        'rotate stick figure
        ActiveSheet.Shapes.Range(Array("stickman")).IncrementRotation 60
        
        'tomato throw; changes coordinates of tomato
        For x = 0 To k
            Range("_x").Value = x
            Range("_y").Value = a * (x - h) ^ 2 + k
            Sleep (25 / Range("throwSpeed"))
            Calculate 'seems to work faster than Application.ScreenUpdating = True
            'Application.Wait Now + ms * Range("throwSpeed").Value
            'DoEvents
        Next
    
        'move splat graphic to end point of throw
        Range("splat_x").Value = Range("_x").Value
        Range("splat_y").Value = Range("_y").Value
        
        'reset stick figure
        ActiveSheet.Shapes.Range(Array("stickman")).IncrementRotation -60
        Calculate 'seems to work faster than Application.ScreenUpdating = True
        
        'set new value for cell total savings number
        PrevVal = Range("actualSavings").Value
    End If
End Sub
