minutes = WScript.Arguments.Item(0)
seconds = minutes * 60

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c timeout /t " & seconds & " /nobreak && rundll32.exe powrprof.dll,SetSuspendState 0,1,0", 0, False